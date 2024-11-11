# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrderTaskMaterial(models.Model):
	"""Modelo para almacenar los materiales de las partida en el pedido"""
	
	_name = 'sale.order.task.material'
	_description = "Sale Order Task Material"
	_order = 'order_id, material_id'
	_check_company_auto = True

	#Campo relación con el pedido
	order_id = fields.Many2one(comodel_name='sale.order', string='Pedido')
	#Material
	material_id = fields.Many2one(comodel_name='product.product', string='Material', store=True, check_company=True)
	#Descripcion del material
	name = fields.Char(
		string='Nombre',)
	#Precios Totales de para cada material
	sale_price = fields.Float(string='P.V.', digits='Product Price', store=True, compute='_compute_price')
	cost_price = fields.Float(string='P.C.', digits='Product Price', store=True, compute='_compute_price')
	#Precios Unitarios para cada material
	sale_price_unit = fields.Float(
		string='P.V.U.', 
        digits='Product Price', store=True)
	cost_price_unit = fields.Float(
		string='P.C.U.', 
        digits='Product Price', store=True)
	#Cantidad de cada material
	quantity = fields.Float(string='Und.', digits='Product Unit of Measure', store=True)
	#Descuento aplicado al precio del material
	discount = fields.Float(string='Des. (%)', digits='Discount', store=True)
	sequence = fields.Integer()
	#Margen
	material_margin = fields.Float(string='Margen', digits='Product Price', compute='_compute_price', store=True)
	material_margin_percent = fields.Float(string='Margen (%)', digits='Product Price', compute='_compute_price', store=True)
	#Misma compañia que el pedido al que pertence
	company_id = fields.Many2one(related='material_id.company_id', store=True, index=True, precompute=True)
	#Misma moneda que el pedido al que pertenece
	currency_id = fields.Many2one(related='material_id.currency_id', depends=['material_id.currency_id'], store=True, precompute=True) 

	#Calculo de los precios de venta y coste totales por linea de los materiales
	@api.depends('quantity','sale_price_unit','cost_price_unit','discount')
	def _compute_price(self):
		self.sale_price = 0.0
		self.cost_price = 0.0
		self.material_margin = 0.0
		self.material_margin_percent = 0.0
		for record in self:
			record.sale_price = record.quantity * (record.sale_price_unit * (1 - (record.discount / 100)))
			record.cost_price = (record.quantity * record.cost_price_unit)
			record.material_margin = (record.quantity * (record.sale_price_unit * (1 - (record.discount / 100)))) - (record.quantity * record.cost_price_unit)
			if (record.sale_price != 0) and (record.cost_price != 0):
				record.material_margin_percent = (1-(record.cost_price/record.sale_price)) 
