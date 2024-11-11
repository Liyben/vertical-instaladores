# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrderTaskWork(models.Model):
	"""Modelo para almacenar los trabajos de las partida en el pedido"""

	_name = 'sale.order.task.work'
	_description = "Sale Order Task Work"
	_order = 'order_id, work_id'
	_check_company_auto = True

	#Campo relación con el pedido
	order_id = fields.Many2one(comodel_name='sale.order', string='Pedido')
	#Mano de obra
	work_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', store=True, check_company=True)
	#Descripcion del trabajo
	name = fields.Char(
		string='Nombre',
		store=True, )
	#Precios Totales para cada trabajo
	sale_price = fields.Float(string='P.V.', digits='Product Price', compute="_compute_price", store=True)
	cost_price = fields.Float(string='P.C.', digits='Product Price', compute="_compute_price", store=True)
	#Precios Unitarios para cada trabajo
	sale_price_unit = fields.Float(
		string='P.V.U.', 
        digits='Product Price',
        store=True)
	cost_price_unit = fields.Float(
		string='P.C.U.', 
        digits='Product Price',
        store=True)
	#Horas empleadas en el trabajo
	hours = fields.Float(string='Hr.', store=True)
	#Descuento aplicado al precio de la mano de obra
	discount = fields.Float(string='Des. (%)', digits='Discount', store=True)
	sequence = fields.Integer()
	#Margen
	work_margin = fields.Float(string='Margen', digits='Product Price', compute='_compute_price', store=True)
	work_margin_percent = fields.Float(string='Margen (%)', digits='Product Price', compute='_compute_price', store=True)
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
