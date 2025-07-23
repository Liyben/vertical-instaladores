# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLineTaskWork(models.Model):
    """Modelo para almacenar los trabajos del producto partida en la linea de pedido"""

    _name = 'sale.order.line.task.work'
    _description = "Sale Order Line Task Work"
    _order = 'order_line_id, sequence, id'
    _check_company_auto = True

    #Dominio para el campo mano de obra
    @api.model
    def _get_work_id_domain(self):
        uom_categ_id = self.env.ref('uom.uom_categ_wtime').id
        return [('uom_id.category_id', '=', uom_categ_id), ('sale_ok', '=', True)]

    #Campo relación con la linea de pedido
    order_line_id = fields.Many2one(comodel_name='sale.order.line', string='Linea de pedido')
    #Mano de obra
    work_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', required=True, domain=_get_work_id_domain, check_company=True)
    #Descripcion del trabajo
    name = fields.Char(
        string='Nombre',
        compute='_compute_name',
        store=True, readonly=False, required=True, precompute=True)
    #Precios Totales para cada trabajo
    sale_price = fields.Float(string='P.V.', digits='Product Price', compute="_compute_price")
    cost_price = fields.Float(string='P.C.', digits='Product Price', compute="_compute_price")
    #Precios Unitarios para cada trabajo
    sale_price_unit = fields.Float(
        string='P.V.U.', 
        digits='Product Price',
        readonly=False, required=True)
    cost_price_unit = fields.Float(
        string='P.C.U.', 
        digits='Product Price',
        readonly=False, required=True)
    #Horas empleadas en el trabajo
    hours = fields.Float(string='Hr.')
    #Descuento aplicado al precio de la mano de obra
    discount = fields.Float(string='Des. (%)', digits='Discount', store=True, precompute=True, compute='_compute_discount')
    sequence = fields.Integer()
    #Margen
    work_margin = fields.Float(string='Margen', digits='Product Price', compute='_compute_price')
    work_margin_percent = fields.Float(string='Margen (%)', digits='Product Price', compute='_compute_price')
    #Misma compañia que el pedido al que pertence
    company_id = fields.Many2one(related='work_id.company_id', store=True, index=True, precompute=True)
    #Misma moneda que el pedido al que pertenece
    currency_id = fields.Many2one(related='work_id.currency_id', depends=['work_id.currency_id'], store=True, precompute=True) 

    #Comprobar si se aplica tarifa o no
    def _check_apply_pricelist(self):
        self.ensure_one()
        self.order_line_id.ensure_one()
        self.order_line_id.product_id.ensure_one()

        return self.order_line_id.product_id.apply_pricelist
    
    #Obtener la fecha del pedido
    def _get_order_date(self):
        self.ensure_one()
        self.order_line_id.ensure_one()

        return self.order_line_id.order_id.date_order
    
    #Calculo del precio unitario según tarifa
    def _get_display_price(self):
        self.ensure_one()
        self.order_line_id.ensure_one()
        self.work_id.ensure_one()

        #Guardamos los precios de la ficha de mano de obra
        product_lst_price = self.work_id.list_price
        product_standard_price = self.work_id.standard_price
        #Actualizamos los precios de la ficha de mano de obra con los precios de la linea de mano de obra
        self.work_id.write({
            'list_price' : self.sale_price_unit,
            'standard_price' : self.cost_price_unit,
            })
        
        #Obtenemos el elemento de tarifa
        pricelist_item_id = self.order_line_id.order_id.pricelist_id._get_product_rule(
            self.work_id,
            quantity=self.hours or 1.0,
            uom=self.work_id.uom_id,
            date=self._get_order_date(),
        )
        
        pricelist_item = self.env['product.pricelist.item'].search([
            ('id', '=', pricelist_item_id)
        ])
        
        #Aplicamos tarifa
        price = pricelist_item._compute_price(
            product=self.work_id,
            quantity=self.hours or 1.0,
            uom=self.work_id.uom_id,
            date=self._get_order_date(),
            currency=self.currency_id,
        )

        if self.order_line_id.order_id.pricelist_id.discount_policy == 'without_discount' or not pricelist_item:
            
            #Recuperamos los precios de la ficha de mano de obra previamente guardado
            self.work_id.write({
                'list_price' : product_lst_price,
                'standard_price' : product_standard_price,
                })
            
            return price
        
        base_price = pricelist_item._compute_price_before_discount(
            product=self.work_id,
            quantity=self.hours or 1.0,
            uom=self.work_id.uom_id,
            date=self._get_order_date(),
            currency=self.currency_id,
        )

        #Recuperamos los precios de la ficha de mano de obra previamente guardado
        self.work_id.write({
            'list_price' : product_lst_price,
            'standard_price' : product_standard_price,
            })
        
        return max(base_price, price)
    
    #Devuelve el precio base
    def _get_pricelist_price_before_discount(self, rec, pricelist_item):
        rec.ensure_one()
        rec.work_id.ensure_one()

        return pricelist_item._compute_price_before_discount(
            product=rec.work_id,
            quantity=rec.hours or 1.0,
            uom=rec.work_id.uom_id,
            date=rec._get_order_date(),
            currency=rec.currency_id,
        )
    
    #Devuelve el precio dado por la tarifa
    def _get_pricelist_price(self, rec, pricelist_item):
        rec.ensure_one()
        rec.work_id.ensure_one()

        price = pricelist_item._compute_price(
            product=rec.work_id,
            quantity=rec.hours or 1.0,
            uom=rec.work_id.uom_id,
            date=rec._get_order_date(),
            currency=rec.currency_id,
        )

        return price
    
    #Calculo del descuento si se aplica tarifa
    @api.depends('work_id')
    def _compute_discount(self):
        for record in self:
            if not record.work_id:
                record.discount = 0.0

            if not (
                record.order_line_id.order_id.pricelist_id 
                and record.order_line_id.order_id.pricelist_id.discount_policy == 'without_discount'
            ):  
                continue
            
            record.discount = 0.0

            #Obtenemos el elemento de tarifa
            pricelist_item_id = record.order_line_id.order_id.pricelist_id._get_product_rule(
                record.work_id,
                quantity=record.hours or 1.0,
                uom=record.work_id.uom_id,
                date=record._get_order_date(),
            )
            
            pricelist_item = self.env['product.pricelist.item'].search([
                ('id', '=', pricelist_item_id)
            ])

            if not pricelist_item:
                continue
            
            record = record.with_company(record.company_id)
            pricelist_price = record._get_pricelist_price(record, pricelist_item)
            base_price = record._get_pricelist_price_before_discount(record, pricelist_item)

            if base_price != 0:
                discount = (base_price - pricelist_price) / base_price * 100
                if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                    record.discount = discount

    #Calculo de los precios de venta y coste totales por linea de los trabajos
    @api.depends('hours','sale_price_unit', 'cost_price_unit', 'discount')
    def _compute_price(self):
        self.sale_price = 0.0
        self.cost_price = 0.0
        self.work_margin = 0.0
        self.work_margin_percent = 0.0
        for record in self:
            record.sale_price = record.hours * (record.sale_price_unit * (1 - (record.discount / 100)))
            record.cost_price = (record.hours * record.cost_price_unit)
            record.work_margin = (record.hours * (record.sale_price_unit * (1 - (record.discount / 100)))) - (record.hours * record.cost_price_unit)

            if (record.sale_price != 0) and (record.cost_price != 0):
                record.work_margin_percent = (1-(record.cost_price/record.sale_price))

    #Carga el nombre de la mano de obra
    @api.depends('work_id')
    def _compute_name(self):
        for record in self:
            if not record.work_id:
                continue
            record.name = record.work_id.name

    #Carga los precios unitarios de la mano de obra
    @api.onchange('work_id')
    def _onchange_price_unit(self):
        for record in self:
            if not record.work_id:
                continue
            record.sale_price_unit = record.work_id.list_price
            record.cost_price_unit = record.work_id.standard_price
            if record._check_apply_pricelist():
                record.sale_price_unit = record._get_display_price()