# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLineTaskMaterial(models.Model):
	"""Modelo para almacenar los materiales del producto partida en la linea de pedido"""
	
	_name = 'sale.order.line.task.material'
	_description = "Sale Order Line Task Material"
	_order = 'order_line_id, sequence, id'
	_check_company_auto = True

	#Dominio para el campo material
	@api.model
	def _get_material_id_domain(self):
		uom_categ_id = self.env.ref('uom.uom_categ_wtime').id
		return [('uom_id.category_id', '!=', uom_categ_id), ('sale_ok', '=', True)]

	#Descripcion del material
	name = fields.Char(
		string='Nombre',
		compute='_compute_name',
		store=True, readonly=False, required=True, precompute=True)
	#Campo relación con la linea de pedido
	order_line_id = fields.Many2one(comodel_name='sale.order.line', string='Linea de pedido')
	#Material
	material_id = fields.Many2one(comodel_name='product.product', string='Material', required=True, domain=_get_material_id_domain, check_company=True)
	#Precios Totales de para cada material
	sale_price = fields.Float(string='P.V.', digits='Product Price', compute='_compute_price')
	cost_price = fields.Float(string='P.C.', digits='Product Price', compute='_compute_price')
	#Precios Unitarios para cada material
	sale_price_unit = fields.Float(
		string='P.V.U.', 
		compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)
	cost_price_unit = fields.Float(
		string='P.C.U.', 
		compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, required=True, precompute=True)
	#Cantidad de cada material
	quantity = fields.Float(string='Und.', digits='Product Unit of Measure', default=1.0)
	#Descuento aplicado al precio del material
	discount = fields.Float(string='Des. (%)', digits='Discount', default=0.0)
	sequence = fields.Integer()
	#Margen
	material_margin = fields.Float(string='Margen', digits='Product Price', compute='_compute_price')
	material_margin_percent = fields.Float(string='Margen (%)', digits='Product Price', compute='_compute_price')
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

	#Carga el nombre de la mano de obra
	@api.depends('material_id')
	def _compute_name(self):
		for record in self:
			if not record.material_id:
				continue
			record.name = record.material_id.name

	#Carga los precios unitarios de la mano de obra
	@api.depends('material_id')
	def _compute_price_unit(self):
		for record in self:
			if not record.material_id:
				continue
			record.sale_price_unit = record.material_id.list_price
			record.cost_price_unit = record.material_id.standard_price