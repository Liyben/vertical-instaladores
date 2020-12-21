# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

class ProductTemplate(models.Model):

	_inherit='product.template'

	#PVP Proveedor y Descuento y Beneficio
	pvp_buy = fields.Float(string='PVP de compra', digits=dp.get_precision('Product Price'))
	pvp_sale = fields.Float(string='PVP de venta', digits=dp.get_precision('Product Price'))
	discount_buy = fields.Float(string='Dto. de compra', digits=dp.get_precision('Product Price'))
	discount_sale = fields.Float(string='Dto. de venta', digits=dp.get_precision('Product Price'))
	benefit = fields.Float(string='Beneficio', digits=dp.get_precision('Product Price'))
	price_sale_based_on = fields.Selection([('benefit', 'Beneficio sobre precio de coste'), ('discount', 'Descuentro sobre PVP de venta')], string='Precio basado en', default='discount', required=True)

	@api.onchange('pvp_buy')
	def _get_standard_price_pvp_buy(self):
		for record in self:
			record.standard_price = record.pvp_buy * (1 -(record.discount_buy/100))

	@api.onchange('discount_buy')
	def _get_standard_price_discount_buy(self):
		for record in self:
			record.standard_price = record.pvp_buy * (1 -(record.discount_buy/100))

	@api.onchange('pvp_sale')
	def _get_standard_price_pvp_sale(self):
		for record in self:
			if record.price_sale_based_on == 'discount':
				record.benefit = 0.0
				record.list_price = record.pvp_sale * (1 -(record.discount_sale/100))

	@api.onchange('discount_sale')
	def _get_standard_price_discount_sale(self):
		for record in self:
			if record.price_sale_based_on == 'discount':
				record.benefit = 0.0
				record.list_price = record.pvp_sale * (1 -(record.discount_sale/100))

	def _compute_benefit(self, allBenefit):
		res = 1
		if allBenefit != 0:
			res = allBenefit
		return res

	@api.onchange('benefit')
	def _get_list_price_benefit(self):
		for record in self:
			if record.price_sale_based_on == 'benefit':
				record.discount_sale = 0.0
				record.list_price = (record.standard_price / self._compute_benefit(1-(record.benefit/100)))

class ProductProduct(models.Model):
	_inherit = "product.product"
	
	@api.onchange('pvp_buy')
	def _get_standard_price_pvp_buy(self):
		for record in self:
			record.standard_price = record.pvp_buy * (1 -(record.discount_buy/100))

	@api.onchange('discount_buy')
	def _get_standard_price_discount_buy(self):
		for record in self:
			record.standard_price = record.pvp_buy * (1 -(record.discount_buy/100))

	@api.onchange('pvp_sale')
	def _get_standard_price_pvp_sale(self):
		for record in self:
			if record.price_sale_based_on == 'discount':
				record.benefit = 0.0
				record.list_price = record.pvp_sale * (1 -(record.discount_sale/100))

	@api.onchange('discount_sale')
	def _get_standard_price_discount_sale(self):
		for record in self:
			if record.price_sale_based_on == 'discount':
				record.benefit = 0.0
				record.list_price = record.pvp_sale * (1 -(record.discount_sale/100))

	def _compute_benefit(self, allBenefit):
		res = 1
		if allBenefit != 0:
			res = allBenefit
		return res

	@api.onchange('benefit')
	def _get_list_price_benefit(self):
		for record in self:
			if record.price_sale_based_on == 'benefit':
				record.discount_sale = 0.0
				record.list_price = (record.standard_price / self._compute_benefit(1-(record.benefit/100)))