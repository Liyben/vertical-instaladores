# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

class ProductTemplate(models.Model):

	_inherit='product.template'

	#Precio sin desperdicio y % desperdicio
	without_waste_price = fields.Float(string='Precio Coste sin desp.', digits='Product Price')
	percent_waste = fields.Float(string='% Desperdicio', digits='Discount')
	
	@api.onchange('without_waste_price')
	def _get_standard_price_without_waste_price(self):
		for record in self:
			record.standard_price = record.without_waste_price + (record.without_waste_price * record.percent_waste / 100)

	@api.onchange('percent_waste')
	def _get_standard_price_percent_waste(self):
		for record in self:
			record.standard_price = record.without_waste_price + (record.without_waste_price * record.percent_waste / 100)

class ProductProduct(models.Model):
	_inherit = "product.product"
	
	@api.onchange('without_waste_price')
	def _get_standard_price_without_waste_price(self):
		for record in self:
			record.standard_price = record.without_waste_price + (record.without_waste_price * record.percent_waste / 100)

	@api.onchange('percent_waste')
	def _get_standard_price_percent_waste(self):
		for record in self:
			record.standard_price = record.without_waste_price + (record.without_waste_price * record.percent_waste / 100)
