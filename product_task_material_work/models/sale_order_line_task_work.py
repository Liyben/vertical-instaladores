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
	discount = fields.Float(string='Des. (%)', digits='Discount', default=0.0)
	sequence = fields.Integer()
	#Margen
	work_margin = fields.Float(string='Margen', digits='Product Price', compute='_compute_price')
	work_margin_percent = fields.Float(string='Margen (%)', digits='Product Price', compute='_compute_price')
	#Misma compañia que el pedido al que pertence
	company_id = fields.Many2one(related='work_id.company_id', store=True, index=True, precompute=True)
	#Misma moneda que el pedido al que pertenece
	currency_id = fields.Many2one(related='work_id.currency_id', depends=['work_id.currency_id'], store=True, precompute=True) 

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