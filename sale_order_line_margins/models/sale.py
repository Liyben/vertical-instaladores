# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class SaleOrderLine(models.Model):

	_inherit='sale.order.line'

	margin_benefit = fields.Float (string='Margen', digits=dp.get_precision('Product Price'))

	@api.onchange('product_id')
	def _onchange_product_id_change_margin_benefit(self):

		for line in self:
			line.margin_benefit = 0.0

	@api.onchange('margin_benefit','purchase_price')
	def  _onchange_margin_benefit(self):
		
		for line in self:
			if line.margin_benefit != 0.0:
				currency = line.order_id.pricelist_id.currency_id
				line.price_unit = currency.round(line.purchase_price / (1-(line.margin_benefit / 100)))
			else: 
				if (line.auto_create_task):
					line._onchange_task_materials_works_workforce()
				else:
					line.product_uom_change()