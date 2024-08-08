# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):

	_inherit='product.template'

	#Campos relacionales para trabajos y materiales
	task_works_ids = fields.One2many(comodel_name='product.task.work', inverse_name='product_id', string='Trabajos', copy=True)
	task_materials_ids = fields.One2many(comodel_name='product.task.material', inverse_name='product_id', string='Materiales', copy=True)
	#Precio totales, unitarios y beneficio de Trabajos
	total_sp_work = fields.Float(string='Total P.V.', digits='Product Price', compute='_compute_total_sp_work')
	total_cp_work = fields.Float(string='Total P.C.', digits='Product Price', compute='_compute_total_cp_work')
	benefit_work = fields.Float(string='Beneficio (%)', compute='_compute_benefit_work', store=True)
	benefit_work_amount = fields.Monetary(string='Beneficio (€)', compute='_compute_benefit_work', store=True)
	total_hours = fields.Float(string='Total horas', compute='_compute_total_hours')
	#Precios totales, unitarios  y beneficio de Materiales
	total_sp_material = fields.Float(string='Total P.V.', digits='Product Price', compute='_compute_total_sp_material')
	total_cp_material = fields.Float(string='Total P.C.', digits='Product Price', compute='_compute_total_cp_material')
	benefit_material = fields.Float(string='Beneficio (%)',  compute='_compute_benefit_material', store=True)
	benefit_material_amount = fields.Monetary(string='Beneficio (€)',  compute='_compute_benefit_material', store=True)
	#Campo boolean para saber si crear o no una tarea de forma automatica
	auto_create_task = fields.Boolean(string='Tarea automática', compute='_compute_auto_create_task')
	#apply_pricelist = fields.Boolean(string='Aplicar tarifa')
	#Campo para calcular el numero de productos compuestos en los que se encuentra
	product_compound_count = fields.Integer(string='Partidas', compute='_compute_product_compound_count')
	#Campo para controlar la visualización de los trabajos y materiales
	see_works_and_materials = fields.Selection([
		('all', 'Trabajos y Materiales'),
		('only_works', 'Solo Trabajos'),
		('only_materials', 'Solo Materiales')],
		string="Ver", default='all')


	@api.onchange('service_tracking')
	def _onchange_service_tracking_2(self):
		if (self.service_tracking == 'task_global_project') or (self.service_tracking == 'task_in_project'):
			self.see_works_and_materials = 'all'
		else:
			self.see_works_and_materials = False

	#Calcula el numero de productos compuestos en los que se encuentra
	def _compute_product_compound_count(self):
		for record in self:
			count = 0
			if record.type == 'service':
				work_ids = self.env["product.task.work"].search([("work_id.product_tmpl_id", "=", record.id)])
				count = len(work_ids)
			else: 
				material_ids = self.env["product.task.material"].search([("material_id.product_tmpl_id", "=", record.id)])
				count = len(material_ids)

			record.product_compound_count = count

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

	#Comprobación de los productos que se encuentran en compuestos
	@api.constrains("active")
	def _check_archive(self):
		for record in self:
			if (self.env["product.task.material"].with_context(active_test=False).search([("material_id", "=", record.id)]) or 
			self.env["product.task.work"].with_context(active_test=False).search([("work_id", "=", record.id)])):

				raise ValidationError(
					_(
						"Este producto se encuentra al menos en un producto tipo partida."
					)
				)

	#Devuelve los valores para la acción de ventana al pulsar en Productos Compuestos
	def action_view_product_compound(self):

		action = self.env.ref('sale.product_template_action').read()[0]

		products_compound = []
		if self.type == 'service':
			works = self.env["product.task.work"].search([("work_id.product_tmpl_id", "=", self.id)])
			products_compound = works.mapped('product_id')
		else: 
			materials = self.env["product.task.material"].search([("material_id.product_tmpl_id", "=", self.id)])
			products_compound = materials.mapped('product_id')

		if len(products_compound) > 1:
			action['views'] = [(self.env.ref('product.product_template_tree_view').id, 'tree'),(self.env.ref('product.product_template_form_view').id, 'form')]
			action['domain'] = [('id', 'in', products_compound.ids)]
		elif products_compound:
			action['views'] = [(self.env.ref('product.product_template_form_view').id, 'form')]
			action['res_id'] = products_compound.id
		return action
			
