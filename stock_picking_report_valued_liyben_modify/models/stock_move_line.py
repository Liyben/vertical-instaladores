# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMoveLine(models.Model):
	_inherit = 'stock.move.line'

	purchase_line = fields.Many2one(
		related='move_id.purchase_line_id', readonly=True,
		string='Linea de pedido de compra relacionada',
		related_sudo=True,  # See explanation for sudo in compute method
	)
	purchase_currency_id = fields.Many2one(
		related='purchase_line.currency_id', readonly=True,
		string='Moneda compra',
		related_sudo=True,
	)
	purchase_tax_id = fields.Many2many(
		related='purchase_line.taxes_id', readonly=True,
		string='Impuestos de compra',
		related_sudo=True,
	)
	purchase_price_unit = fields.Float(
		related='purchase_line.price_unit', readonly=True,
		string='Precio compra',
		related_sudo=True,
	)
	purchase_discount = fields.Float(
		related='purchase_line.discount', readonly=True,
		string='Descuento compra (%)',
		related_sudo=True,
	)
	purchase_tax_description = fields.Char(
		compute='_compute_purchase_order_line_fields',
		string='Descripcion de impuestos',
		compute_sudo=True,  # See explanation for sudo in compute method
	)
	purchase_price_subtotal = fields.Monetary(
		compute='_compute_purchase_order_line_fields',
		string='Subtotal ompra',
		compute_sudo=True,
	)
	purchase_price_tax = fields.Float(
		compute='_compute_purchase_order_line_fields',
		string='Impuestos compra',
		compute_sudo=True,
	)
	purchase_price_total = fields.Monetary(
		compute='_compute_purchase_order_line_fields',
		string='Total compra',
		compute_sudo=True,
	)

	@api.multi
	def _compute_purchase_order_line_fields(self):
		"""This is computed with sudo for avoiding problems if you don't have
		access to sales orders (stricter warehouse users, inter-company
		records...).
		"""
		for line in self:
			purchase_line = line.purchase_line
			price_unit = (
				purchase_line.price_subtotal / purchase_line.product_qty
				if purchase_line.product_qty else purchase_line.price_unit)
			taxes = line.purchase_tax_id.compute_all(
				price_unit=price_unit,
				currency=line.purchase_currency_id,
				quantity=line.qty_done or line.product_qty,
				product=line.product_id,
				partner=purchase_line.order_id.partner_id)
			if purchase_line.company_id.tax_calculation_rounding_method == (
					'round_globally'):
				price_tax = sum(
					t.get('amount', 0.0) for t in taxes.get('taxes', []))
			else:
				price_tax = taxes['total_included'] - taxes['total_excluded']
			line.update({
				'purchase_tax_description': ', '.join(
					t.name or t.description for t in line.purchase_tax_id),
				'purchase_price_subtotal': taxes['total_excluded'],
				'purchase_price_tax': price_tax,
				'purchase_price_total': taxes['total_included'],
			})