# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

		
class ProdcutTaskWork(models.Model):
	""" Modelo para almacenar los trabajos en la partida del producto"""

	_name = 'product.task.work'
	_description = "Product Task Work"
	_order = 'sequence'
	_check_company_auto = True

	#Dominio para el campo mano de obra
	@api.model
	def _get_work_id_domain(self):
		uom_categ_id = self.env.ref('uom.uom_categ_wtime').id
		return [('uom_id.category_id', '=', uom_categ_id), ('sale_ok', '=', True)]

	#Campo relación con el producto de la partida
	product_id = fields.Many2one(comodel_name='product.template', string='Producto', ondelete='restrict')
	#Mano de obra
	work_id = fields.Many2one(
		comodel_name='product.product', string='Mano de obra', required=True, domain=_get_work_id_domain, check_company=True
		)
	#Descripcion del trabajo
	name = fields.Char(string='Nombre', required=True)
	#Precios Totales para cada trabajo
	sale_price = fields.Float(string='P.V.', digits='Product Price', compute="_compute_price")
	cost_price = fields.Float(string='P.C.', digits='Product Price', compute="_compute_price")
	#Precios Unitarios para cada material
	sale_price_unit = fields.Float(string='P.V.U.', digits='Product Price', compute='_compute_price')
	cost_price_unit = fields.Float(string='P.C.U.', digits='Product Price', compute='_compute_price')
	#Horas empleadas en el trabajo
	hours = fields.Float(string='Hr.')
	sequence = fields.Integer()
	#Margen
	work_margin = fields.Monetary(string='Margen', digits='Product Price', compute='_compute_price')
	work_margin_percent = fields.Float(string='Margen (%)', digits='Product Price', compute='_compute_price')
	#Misma compañia que el producto partida al que pertence
	company_id = fields.Many2one(related='product_id.company_id', string='Company', store=True, readonly=True, index=True)
	#Misma moneda que el producto partida al que pertenece
	currency_id = fields.Many2one(related='product_id.currency_id', depends=['product_id.currency_id'], store=True, precompute=True)


	#Calcula el valor para todos los precios de cada linea de trabajo
	
	@api.depends('hours','work_id')
	def _compute_price(self):
		self.sale_price_unit = 0.0
		self.cost_price_unit = 0.0
		self.sale_price = 0.0
		self.cost_price = 0.0
		self.work_margin = 0.0
		self.work_margin_percent = 0.0
		for record in self:
			record.sale_price_unit = record.work_id.list_price
			record.cost_price_unit = record.work_id.standard_price
			record.sale_price = (record.hours * record.work_id.list_price)
			record.cost_price = (record.hours * record.work_id.standard_price)
			record.work_margin = (record.hours * record.work_id.list_price) - (record.hours * record.work_id.standard_price)
			if (record.sale_price != 0) and (record.cost_price != 0):
				record.work_margin_percent = (1-(record.cost_price/record.sale_price))

	#Carga el nombre de la mano de obra
	@api.onchange('work_id')
	def _onchange_work_id(self):
		for record in self:
			record.name = record.work_id.name


	
		
