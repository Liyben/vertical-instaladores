# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _


class ProductTaskMaterial(models.Model):
	"""Modelo para almacenar los materiales en la partida del producto"""
	
	_name = 'product.task.material'
	_description = "Product Task Material"
	_order = 'sequence'
	_check_company_auto = True

	#Dominio para el campo material
	@api.model
	def _get_material_id_domain(self):
		uom_categ_id = self.env.ref('uom.uom_categ_wtime').id
		return [('uom_id.category_id', '!=', uom_categ_id, ('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', self.company_id))]

	#Descripcion del material
	name = fields.Char(string='Descripción', required=True)
	#Campo relación con el producto de la partida
	product_id = fields.Many2one(comodel_name='product.template', string='Producto',ondelete='restrict')
	#Material
	material_id = fields.Many2one(
		comodel_name='product.product', string='Material', required=True, domain=_get_material_id_domain, check_company=True
		)
	#Precios Totales de para cada material
	sale_price = fields.Float(string='P.V.', digits='Product Price', compute='_compute_price')
	cost_price = fields.Float(string='P.C.', digits='Product Price', compute='_compute_price')
	#Precios Unitarios para cada material
	sale_price_unit = fields.Float(string='P.V.U.', digits='Product Price', compute='_compute_price')
	cost_price_unit = fields.Float(string='P.C.U.', digits='Product Price', compute='_compute_price')
	#Cantidad de cada material
	quantity = fields.Float(string='Und.', digits='Product Unit of Measure')
	sequence = fields.Integer()
	#Margen
	material_margin = fields.Monetary(string='Margen', digits='Product Price', compute='_compute_price', store=True)
	material_margin_percent = fields.Float(string='Margen (%)', digits='Product Price', compute='_compute_price', store=True)
	#Misma compañia que el producto partida al que pertence
	company_id = fields.Many2one(related='product_id.company_id', string='Company', store=True, readonly=True, index=True)
	#Misma moneda que el producto partida al que pertenece
	currency_id = fields.Many2one(related='product_id.currency_id', depends=['product_id.currency_id'], store=True, precompute=True)

	#Calcula el valor de todos los precios de cada linea del material
	@api.depends('quantity','material_id')
	def _compute_price(self):
		self.sale_price_unit = 0.0
		self.cost_price_unit = 0.0
		self.sale_price = 0.0
		self.cost_price = 0.0
		self.material_margin = 0.0
		self.material_margin_percent = 0.0
		for record in self:
			record.sale_price_unit = record.material_id.list_price
			record.cost_price_unit = record.material_id.standard_price
			record.sale_price = (record.quantity * record.material_id.list_price)
			record.cost_price = (record.quantity * record.material_id.standard_price)
			record.material_margin = (record.quantity * record.material_id.list_price) - (record.quantity * record.material_id.standard_price)
			if (record.sale_price != 0) and (record.cost_price != 0):
				record.material_margin_percent = (1-(record.cost_price/record.sale_price))
	
	#Carga el nombre del material
	@api.onchange('material_id')
	def _onchange_work_id(self):
		for record in self:
			record.name = record.material_id.name
	
		
