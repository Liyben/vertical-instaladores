# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = [
        _name,
        "stock.invoice.state.mixin",
    ]
 
    """ currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_currency_id',
        string='Moneda',
        compute_sudo=True,
    ) """
    
    #Campos para modelo sale.order.line 
    sale_tax_id = fields.Many2many(
        related='sale_line_id.tax_id', readonly=True,
        string='Impuesto',
        related_sudo=True,
    )
    sale_price_unit = fields.Float(
        related='sale_line_id.price_unit', readonly=True,
        string='Precio unidad',
        related_sudo=True,
    )
    sale_discount = fields.Float(
        related='sale_line_id.discount', readonly=True,
        string='Descuento (%)',
        related_sudo=True,
    )
    sale_price_subtotal = fields.Monetary(
        compute='_compute_sale_order_line_fields',
        string='Subtotal',
        compute_sudo=True,
    )
    sale_price_tax = fields.Float(
        compute='_compute_sale_order_line_fields',
        string='Impuestos',
        compute_sudo=True,
    )
    sale_price_total = fields.Monetary(
        compute='_compute_sale_order_line_fields',
        string='Total',
        compute_sudo=True,
    )

    #Campos para modelo purchase.order.line
    purchase_tax_id = fields.Many2many(
        related='purchase_line_id.taxes_id', readonly=True,
        string='Impuesto',
        related_sudo=True,
    )
    purchase_price_unit = fields.Float(
        related='purchase_line_id.price_unit', readonly=True,
        string='Precio unidad',
        related_sudo=True,
    )
    purchase_discount = fields.Float(
        related='purchase_line_id.discount', readonly=True,
        string='Descuento (%)',
        related_sudo=True,
    )
    purchase_price_subtotal = fields.Monetary(
        compute='_compute_purchase_order_line_fields',
        string='Subtotal',
        compute_sudo=True,
    )
    purchase_price_tax = fields.Float(
        compute='_compute_purchase_order_line_fields',
        string='Impuestos',
        compute_sudo=True,
    )
    purchase_price_total = fields.Monetary(
        compute='_compute_purchase_order_line_fields',
        string='Total',
        compute_sudo=True,
    )

    """ @api.depends('sale_line_id','purchase_line_id')
    def _compute_currency_id(self):
        res={}
        for line in self:
            if line.sale_line_id:
                res = line.sale_line_id.currency_id
            if line.purchase_line_id:
                res = line.purchase_line_id.currency_id
        return res """

    @api.depends('sale_line_id')
    def _compute_sale_order_line_fields(self):
        """This is computed with sudo for avoiding problems if you don't have
        access to sales orders (stricter warehouse users, inter-company
        records...).
        """
        for line in self:
            sale_line = line.sale_line_id
            price_unit = (
                sale_line.price_subtotal / sale_line.product_uom_qty
                if sale_line.product_uom_qty else sale_line.price_reduce)
            taxes = line.sale_tax_id.compute_all(
                price_unit=price_unit,
                currency=sale_line.currency_id,
                quantity=line.quantity_done or line.product_qty,
                product=line.product_id,
                partner=sale_line.order_id.partner_shipping_id)
            if sale_line.company_id.tax_calculation_rounding_method == (
                    'round_globally'):
                price_tax = sum(
                    t.get('amount', 0.0) for t in taxes.get('taxes', []))
            else:
                price_tax = taxes['total_included'] - taxes['total_excluded']
            line.update({
                'sale_price_subtotal': taxes['total_excluded'],
                'sale_price_tax': price_tax,
                'sale_price_total': taxes['total_included'],
            })

    @api.depends('purchase_line_id')
    def _compute_purchase_order_line_fields(self):
        """This is computed with sudo for avoiding problems if you don't have
        access to purchase orders (stricter warehouse users, inter-company
        records...).
        """
        for line in self:
            purchase_line = line.purchase_line_id
            price_unit = (
                    purchase_line.price_subtotal / purchase_line.product_qty 
                    if purchase_line.product_qty else purchase_line.price_unit)
            taxes = line.sale_tax_id.compute_all(
                price_unit=price_unit,
                currency=purchase_line.currency_id,
                quantity=line.quantity_done or line.product_qty,
                product=line.product_id,
                partner=purchase_line.order_id.partner_id)
            if purchase_line.company_id.tax_calculation_rounding_method == (
                    'round_globally'):
                price_tax = sum(
                    t.get('amount', 0.0) for t in taxes.get('taxes', []))
            else:
                price_tax = taxes['total_included'] - taxes['total_excluded']
            line.update({
                'purchase_price_subtotal': taxes['total_excluded'],
                'purchase_price_tax': price_tax,
                'purchase_price_total': taxes['total_included'],
            })

    def _get_taxes(self, fiscal_position, inv_type):
        """
        Map product taxes based on given fiscal position
        :param fiscal_position: account.fiscal.position recordset
        :param inv_type: string
        :return: account.tax recordset
        """
        if self.sale_line_id:
            taxes = self.sale_tax_id
        elif self.purchase_line_id:
            taxes = self.purchase_tax_id
        else:
            product = self.mapped("product_id")
            product.ensure_one()
            if inv_type in ('out_invoice', 'out_refund'):
                taxes = product.taxes_id
            else:
                taxes = product.supplier_taxes_id
        company_id = self.env.context.get(
                'force_company', self.env.user.company_id.id)

        my_taxes = taxes.filtered(lambda r: r.company_id.id == company_id)
        return fiscal_position.map_tax(my_taxes)

    def _get_price_unit_invoice(self, inv_type, partner, qty=1):
        """
        Gets price unit for invoice
        :param inv_type: str
        :param partner: res.partner
        :param qty: float
        :return: float
        """
        if self.sale_line_id:
            result = self.sale_price_unit
        elif self.purchase_line_id:
           result = self.purchase_price_unit
        else: 
            product = self.mapped("product_id")
            product.ensure_one()
            if inv_type in ('in_invoice', 'in_refund'):
                result = product.price
            else:
                # If partner given, search price in its sale pricelist
                if partner and partner.property_product_pricelist:
                    product = product.with_context(
                        partner=partner.id,
                        quantity=qty,
                        pricelist=partner.property_product_pricelist.id,
                        uom=fields.first(self).product_uom.id
                    )
                    result = product.price
                else:
                    result = product.lst_price

        return result

    def _get_discount(self, inv_type):
        
        if self.sale_line_id:
            result = self.sale_discount
        elif self.purchase_line_id:
            result = self.purchase_discount
        else:
            result = 0
        return result
