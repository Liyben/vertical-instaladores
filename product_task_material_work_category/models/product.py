# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class ProductTemplate(models.Model):

	_inherit='product.template'

	#Check para indicar si se aplica la tarifa definida sobre la categoria del compuesto en los materiales y mano de obra de dicho compuesto
	apply_category = fields.Boolean(string='Aplicar tarifa del compuesto')
	# % desperdicio
	percent_waste = fields.Float(string='% Desperdicio', digits='Discount')
	
	#Función que recalcula el precio de venta y coste del articulo partida a partir de los totales de venta y coste
	
	def product_action_recalculate(self):
		self.list_price = 0.0
		self.standard_price = 0.0
		for record in self:
			record.list_price = record.total_sp_work + record.total_sp_material
			record.standard_price = record.total_cp_work + record.total_cp_material + (((record.total_cp_work + record.total_cp_material) * record.percent_waste) / 100)

class ProductProduct(models.Model):
	_inherit = "product.product"
	
	#Función que recalcula el precio de venta y coste del articulo partida a partir de los totales de venta y coste
	
	def product_action_recalculate(self):
		self.list_price = 0.0
		self.standard_price = 0.0
		for record in self:
			record.list_price = record.total_sp_work + record.total_sp_material
			record.standard_price = record.total_cp_work + record.total_cp_material + (((record.total_cp_work + record.total_cp_material) * record.percent_waste) / 100)
