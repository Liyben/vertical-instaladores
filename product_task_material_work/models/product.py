# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp

class ProductTemplate(models.Model):

	_inherit='product.template'

	#Campos relacionales para trabajos y materiales
	task_works_ids = fields.One2many(comodel_name='product.task.work', inverse_name='product_id', string='Trabajos', copy=True)
	task_materials_ids = fields.One2many(comodel_name='product.task.material', inverse_name='product_id', string='Materiales', copy=True)
	#Producto mano de obra
	workforce_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', copy=True)
	#Precio totales, unitarios y beneficio de Trabajos
	total_sp_work = fields.Float(string='Total P.V.', digits='Product Price', compute='_compute_total_sp_work')
	total_cp_work = fields.Float(string='Total P.C.', digits='Product Price', compute='_compute_total_cp_work')
	benefit_work = fields.Float(string='Beneficio (%)', compute='_compute_benefit_work')
	benefit_work_amount = fields.Float(string='Beneficio (€)', compute='_compute_benefit_work')
	total_hours = fields.Float(string='Total horas', compute='_compute_total_hours')
	#Precios totales, unitarios  y beneficio de Materiales
	total_sp_material = fields.Float(string='Total P.V.', digits='Product Price', compute='_compute_total_sp_material')
	total_cp_material = fields.Float(string='Total P.C.', digits='Product Price', compute='_compute_total_cp_material')
	benefit_material = fields.Float(string='Beneficio (%)',  compute='_compute_benefit_material')
	benefit_material_amount = fields.Float(string='Beneficio (€)',  compute='_compute_benefit_material')
	#Campo boolean para saber si crear o no una tarea de forma automatica
	auto_create_task = fields.Boolean(string='Tarea automática', compute='_compute_auto_create_task')
	apply_pricelist = fields.Boolean(string='Aplicar tarifa')

	#Calcula el total de horas del campo Trabajos
	
	@api.depends('task_works_ids', 'task_works_ids.hours')
	def _compute_total_hours(self):
		self.total_hours = 0.0
		for record in self:
			if record.task_works_ids:
				record.total_hours = sum(record.task_works_ids.mapped('hours'))

	#Define el valor para crear o no una tarea de forma automática
	
	@api.depends('service_tracking')
	def _compute_auto_create_task(self):
		self.auto_create_task = False
		for record in self:
			record.auto_create_task = (record.service_tracking == 'task_global_project') or (record.service_tracking == 'task_in_project')

	#Calcula el precio de venta total del campo Trabajos
	
	@api.depends('task_works_ids', 'task_works_ids.sale_price')
	def _compute_total_sp_work(self):
		self.total_sp_work = 0.0
		for record in self:
			if record.task_works_ids:
				record.total_sp_work = sum(record.task_works_ids.mapped('sale_price'))

	#Calcula el precio de coste total del campo Trabajos
	
	@api.depends('task_works_ids', 'task_works_ids.cost_price')
	def _compute_total_cp_work(self):
		self.total_cp_work = 0.0
		for record in self:
			if record.task_works_ids:
				record.total_cp_work = sum(record.task_works_ids.mapped('cost_price'))

	#Calcula el beneficio de los Trabajos a partir del precio total de venta y coste 
	
	@api.depends('total_sp_work', 'total_cp_work')
	def _compute_benefit_work(self):
		self.benefit_work = 0.0
		self.benefit_work_amount = 0.0
		for record in self:
			record.benefit_work_amount = record.total_sp_work - record.total_cp_work
			if (record.total_sp_work != 0) and (record.total_cp_work != 0):
				record.benefit_work = (1-(record.total_cp_work/record.total_sp_work))

	#Calcula el precio de venta total del campo Materiales
	
	@api.depends('task_materials_ids', 'task_materials_ids.sale_price')
	def _compute_total_sp_material(self):
		self.total_sp_material = 0.0
		for record in self:
			if record.task_materials_ids:
				record.total_sp_material = sum(record.task_materials_ids.mapped('sale_price'))

	#Calcula el precio de coste total del campo Materiales
	
	@api.depends('task_materials_ids', 'task_materials_ids.cost_price')
	def _compute_total_cp_material(self):
		self.total_cp_material = 0.0
		for record in self:
			if record.task_materials_ids:
				record.total_cp_material = sum(record.task_materials_ids.mapped('cost_price'))

	#Calcula el beneficio de los Materiales a partir del precio total de venta y coste
	
	@api.depends('total_sp_material', 'total_cp_material')
	def _compute_benefit_material(self):
		self.benefit_material = 0.0
		self.benefit_material_amount = 0.0
		for record in self:
			record.benefit_material_amount = record.total_sp_material - record.total_cp_material
			if (record.total_cp_material != 0) and (record.total_sp_material != 0):
				record.benefit_material = (1-(record.total_cp_material/record.total_sp_material))

	#Función que recalcula el precio de venta y coste del articulo partida a partir de los totales de venta y coste
	
	def product_action_recalculate(self):
		self.list_price = 0.0
		self.standard_price = 0.0
		for record in self:
			record.list_price = record.total_sp_work + record.total_sp_material
			record.standard_price = record.total_cp_work + record.total_cp_material

	#Carga las lineas de los Trabajos con el precio de venta y coste de un producto mano de obra generico
	#@api.onchange('workforce_id')
	#def _onchange_workforce_id(self):
	#	if self.task_works_ids:
	#		for record in self.task_works_ids:
	#			record.sale_price = (record.hours * record.product_id.workforce_id.list_price)
	#			record.cost_price = (record.hours * record.product_id.workforce_id.standard_price)

class ProductProduct(models.Model):

	_inherit='product.product'

	#Función que recalcula el precio de venta y coste del articulo partida a partir de los totales de venta y coste
	
	def product_action_recalculate(self):
		self.list_price = 0.0
		self.standard_price = 0.0
		for record in self:
			record.list_price = record.total_sp_work + record.total_sp_material
			record.standard_price = record.total_cp_work + record.total_cp_material

			
class ProdcutTaskWork(models.Model):
	""" Modelo para almacenar los trabajos en la partida del producto"""

	_name = 'product.task.work'
	_order = 'sequence'

	#Dominio para el campo mano de obra
	@api.model
	def _get_work_id_domain(self):
		uom_categ_id = self.env.ref('uom.uom_categ_wtime')
		uom_ids = self.env["uom.uom"].search(["category_id", "=", uom_categ_id])
		return [('uom_id', 'in', uom_ids)]

	#Campo relación con el producto de la partida
	product_id = fields.Many2one(comodel_name='product.template', string='Producto', ondelete='restrict')
	#Mano de obra
	work_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', required=True, domain=_get_work_id_domain)
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
	work_margin = fields.Float(string='Margen', digits='Product Price', compute='_compute_price')


	#Calcula el valor para todos los precios de cada linea de trabajo
	
	@api.depends('hours','work_id')
	def _compute_price(self):
		self.sale_price_unit = 0.0
		self.cost_price_unit = 0.0
		self.sale_price = 0.0
		self.cost_price = 0.0
		self.work_margin = 0.0
		for record in self:
			record.sale_price_unit = record.work_id.list_price
			record.cost_price_unit = record.work_id.standard_price
			record.sale_price = (record.hours * record.work_id.list_price)
			record.cost_price = (record.hours * record.work_id.standard_price)
			record.work_margin = (record.hours * record.work_id.list_price) - (record.hours * record.work_id.standard_price)

	#Carga el nombre de la mano de obra
	@api.onchange('work_id')
	def _onchange_work_id(self):
		for record in self:
			record.name = record.work_id.name

class ProductTaskMaterial(models.Model):
	"""Modelo para almacenar los materiales en la partida del producto"""
	
	_name = 'product.task.material'
	_order = 'sequence'

	#Dominio para el campo material
	@api.model
	def _get_material_id_domain(self):
		uom_categ_id = self.env.ref('uom.uom_categ_wtime')
		uom_ids = self.env["uom.uom"].search(["category_id", "=", uom_categ_id])
		return [('uom_id', 'not in', uom_ids)]

	#Descripcion del material
	name = fields.Char(string='Descripción', required=True)
	#Campo relación con el producto de la partida
	product_id = fields.Many2one(comodel_name='product.template', string='Producto',ondelete='restrict')
	#Material
	material_id = fields.Many2one(comodel_name='product.product', string='Material', required=True, domain=_get_material_id_domain)
	#Precios Totales de para cada material
	sale_price = fields.Float(string='P.V.', digits='Product Price', compute='_compute_price')
	cost_price = fields.Float(string='P.C.', digits='Product Price', compute='_compute_price')
	#Precios Unitarios para cada material
	sale_price_unit = fields.Float(string='P.V.U.', digits='Product Price', compute='_compute_price')
	cost_price_unit = fields.Float(string='P.C.U.', digits='Product Price', compute='_compute_price')
	#Cantidad de cada material
	quantity = fields.Float(string='Und.', digits=dp.get_precision('Product Unit of Measure'))
	sequence = fields.Integer()
	#Margen
	material_margin = fields.Float(string='Margen', digits='Product Price', compute='_compute_price')

	#Calcula el valor de todos los precios de cada linea del material
	
	@api.depends('quantity','material_id')
	def _compute_price(self):
		self.sale_price_unit = 0.0
		self.cost_price_unit = 0.0
		self.sale_price = 0.0
		self.cost_price = 0.0
		self.material_margin = 0.0
		for record in self:
				record.sale_price_unit = record.material_id.list_price
				record.cost_price_unit = record.material_id.standard_price
				record.sale_price = (record.quantity * record.material_id.list_price)
				record.cost_price = (record.quantity * record.material_id.standard_price)
				record.material_margin = (record.quantity * record.material_id.list_price) - (record.quantity * record.material_id.standard_price)
	
	#Carga el nombre del material
	@api.onchange('material_id')
	def _onchange_work_id(self):
		for record in self:
			record.name = record.material_id.name
	
		
