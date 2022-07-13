# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp

class AccountMove(models.Model):

	_inherit='account.move'

	#Numero de cliente
	customer_code = fields.Char(related='partner_id.ref', readonly=True, string='Nº. Cliente')

	def public_recompute_dynamic_lines(self):
		self._onchange_invoice_line_ids()

class AccountMoveLine(models.Model):

	_inherit='account.move.line'

	
	#Campos relacionales para trabajos y materiales
	task_works_ids = fields.One2many(comodel_name='account.move.line.task.work', inverse_name='account_move_line_id', string='Trabajos', copy=True)
	task_materials_ids = fields.One2many(comodel_name='account.move.line.task.material', inverse_name='account_move_line_id', string='Materiales', copy=True)
	#Producto mano de obra
	workforce_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', copy=True)
	#Precio totales, unitarios y beneficio de Trabajos
	total_sp_work = fields.Float(string='Total P.V.', digits='Product Price', compute='_compute_total_sp_work', default=0.0)
	total_cp_work = fields.Float(string='Total P.C.', digits='Product Price', compute='_compute_total_cp_work', default=0.0)
	benefit_work = fields.Float(string='Beneficio (%)', digits='Product Price', compute='_compute_benefit_work', default=0.0)
	benefit_work_amount = fields.Float(string='Beneficio (€)', digits='Product Price', compute='_compute_benefit_work', default=0.0)
	total_hours = fields.Float(string='Total horas', compute='_compute_total_hours')
	#Precios totales, unitarios  y beneficio de Materiales
	total_sp_material = fields.Float(string='Total P.V.', digits='Product Price', compute='_compute_total_sp_material', default=0.0)
	total_cp_material = fields.Float(string='Total P.C.', digits='Product Price', compute='_compute_total_cp_material', default=0.0)
	benefit_material = fields.Float(string='Beneficio (%)', digits='Product Price', compute='_compute_benefit_material', default=0.0)
	benefit_material_amount = fields.Float(string='Beneficio (€)', digits='Product Price', compute='_compute_benefit_material', default=0.0)
	#Campo boolean para saber si crear o no una tarea de forma automatica
	auto_create_task = fields.Boolean(string='Tarea automática', copy=True)
	#Opciones de impresión por linea de pedido
	detailed_time = fields.Boolean(string='Imp. horas')
	detailed_price_time = fields.Boolean(string='Imp. precio Hr.')
	detailed_materials = fields.Boolean(string='Imp.materiales')
	detailed_price_materials = fields.Boolean(string='Imp. precio Mat.')
	detailed_subtotal_price_time = fields.Boolean(string='Imp. subtotal Hr.')
	detailed_subtotal_price_materials = fields.Boolean(string='Imp. subtotal Mat.')


	#Carga de los datos del producto en la linea de factura al seleccionar dicho producto
	@api.onchange('product_id')
	def _onchange_product_id(self):
		res = super(AccountMoveLine, self)._onchange_product_id()
		product = self.product_id
		if product:
			self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_in_project')

		if self.auto_create_task:
			work_list = []
			for work in product.task_works_ids:
				work_list.append((0,0, {
					'name' : work.name,
					'work_id': work.work_id.id,
					'sale_price_unit' : work.sale_price_unit,
					'cost_price_unit' : work.cost_price_unit,
					'hours' : work.hours
					}))
			material_list = []
			for material in product.task_materials_ids:
				material_list.append((0,0, {
					'material_id' : material.material_id.id,
					'name': material.name,
					'sale_price_unit' : material.sale_price_unit,
					'cost_price_unit' : material.cost_price_unit,
					'quantity' : material.quantity
					}))
			self.update({'task_works_ids' : work_list,
					'task_materials_ids' : material_list,
					#'workforce_id' : product.workforce_id.id,
					'auto_create_task' : True})
		else:
			self.update({'task_works_ids' : False,
					'task_materials_ids' : False,
					#'workforce_id' : False,
					'auto_create_task' : False})
		return res


	#Calculo del precio total de venta de los trabajos
	
	@api.depends('task_works_ids', 'task_works_ids.sale_price')
	def _compute_total_sp_work(self):
		self.total_sp_work = 0.0
		for record in self:
			if record.task_works_ids:
				record.total_sp_work = sum(record.task_works_ids.mapped('sale_price'))

	#Calculo del precio total de coste de los trabajos
	
	@api.depends('task_works_ids', 'task_works_ids.cost_price')
	def _compute_total_cp_work(self):
		self.total_cp_work = 0.0
		for record in self:
			if record.task_works_ids:
				record.total_cp_work = sum(record.task_works_ids.mapped('cost_price'))

	#Calculo del total de horas de los trabajos
	
	@api.depends('task_works_ids', 'task_works_ids.hours')
	def _compute_total_hours(self):
		self.total_hours = 0.0
		for record in self:
			if record.task_works_ids:
				record.total_hours = sum(record.task_works_ids.mapped('hours'))

	#Calculo del beneficio de los trabajos
	
	@api.depends('total_sp_work', 'total_cp_work')
	def _compute_benefit_work(self):
		self.benefit_work = 0.0
		self.benefit_work_amount = 0.0
		for record in self:
			record.benefit_work_amount = record.total_sp_work - record.total_cp_work
			if (record.total_sp_work != 0) and (record.total_cp_work != 0):
				record.benefit_work = (1-(record.total_cp_work/record.total_sp_work))
			
	#Calculo del precio total de venta de los materiales
	
	@api.depends('task_materials_ids', 'task_materials_ids.sale_price')
	def _compute_total_sp_material(self):
		self.total_sp_material = 0.0
		for record in self:
			if record.task_materials_ids:
				record.total_sp_material = sum(record.task_materials_ids.mapped('sale_price'))

	#Calculo del precio total de coste de los materiales
	
	@api.depends('task_materials_ids', 'task_materials_ids.cost_price')
	def _compute_total_cp_material(self):
		self.total_cp_material = 0.0
		for record in self:
			if record.task_materials_ids:
				record.total_cp_material = sum(record.task_materials_ids.mapped('cost_price'))

	#Calculo del beneficio de los materiales
	
	@api.depends('total_sp_material', 'total_cp_material')
	def _compute_benefit_material(self):
		self.benefit_material = 0.0
		self.benefit_material_amount = 0.0
		for record in self:
			record.benefit_material_amount = record.total_sp_material - record.total_cp_material
			if (record.total_cp_material != 0) and (record.total_sp_material != 0):
				record.benefit_material = (1-(record.total_cp_material/record.total_sp_material))

	#Cambio de los precios unitarios de los trabajos al seleccionar la mano de obra
	#@api.onchange('workforce_id')
	#def _onchange_workforce_id(self):
	#	if self.task_works_ids:
	#		for record in self.task_works_ids:
	#			record.sale_price_unit = record.account_invoice_line_id.workforce_id.list_price
	#			record.cost_price_unit = record.account_invoice_line_id.workforce_id.standard_price

	#Calculo del precio de venta del prodcuto tipo partida en la linea de pedido
	#al producirse algun cambio en los materiales, trabajos o mano de obra
	
	@api.onchange('task_materials_ids', 'task_works_ids')
	def _onchange_task_materials_works_workforce(self):
		for line in self:
			line.price_unit = (line.total_sp_material + line.total_sp_work)
			#line.purchase_price = (line.total_cp_material + line.total_cp_work)

	#Abre la linea de factura en un formulario en primer plano
	def action_invoice_line_open(self):
		invoice_line_form = self.env.ref('product_task_material_work.view_invoice_line_form', False)
		return {
				'type': 'ir.actions.act_window',
				'name': _('Linea de factura'),
				'res_model': 'account.move.line',
				'res_id': self.id,
				'view_type': 'form',
				'view_mode': 'form',
				'views': [(invoice_line_form.id, 'form')],
            	'view_id': invoice_line_form.id,
				'target': 'current',
				'context': '{"check_move_validity": False,}'}

class AccountMoveLineTaskWork(models.Model):
	"""Modelo para almacenar los trabajos del producto partida en la linea de factura"""

	_name = 'account.move.line.task.work'
	_order = 'account_move_line_id, sequence, id'

	#Dominio para el campo mano de obra
	@api.model
	def _get_work_id_domain(self):
		uom_categ_id = self.env.ref('uom.uom_categ_wtime').id
		return [('uom_id.category_id', '=', uom_categ_id)]

	#Campo relación con la linea de factura
	account_move_line_id = fields.Many2one(comodel_name='account.move.line', string='Linea de pedido')
	#Mano de obra
	work_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', required=True, domain=_get_work_id_domain)
	#Descripcion del trabajo
	name = fields.Char(string='Nombre', required=True)
	#Precios Totales para cada trabajo
	sale_price = fields.Float(string='P.V.', digits=dp.get_precision('Product Price'), compute="_compute_price")
	cost_price = fields.Float(string='P.C.', digits=dp.get_precision('Product Price'), compute="_compute_price")
	#Precios Unitarios para cada trabajo
	sale_price_unit = fields.Float(string='P.V.U.', digits=dp.get_precision('Product Price'))
	cost_price_unit = fields.Float(string='P.C.U.', digits=dp.get_precision('Product Price'))
	#Horas empleadas en el trabajo
	hours = fields.Float(string='Hr.')
	#Descuento aplicado al precio de la mano de obra
	discount = fields.Float(string='Des. (%)', digits=dp.get_precision('Discount'), default=0.0)
	#Margen
	work_margin = fields.Float(string='Margen', digits='Product Price', compute='_compute_price')
	work_margin_percent = fields.Float(string='Margen (%)', digits='Product Price', compute='_compute_price')

	sequence = fields.Integer()

	#Carga de los valores en la linea de la mano de obra seleccionada
	
	@api.onchange('work_id')
	def _onchange_work_id(self):
		for record in self:
			record.sale_price_unit = record.work_id.list_price
			record.cost_price_unit = record.work_id.standard_price
			record.name = record.work_id.name

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

class AccountMoveLineTaskMaterial(models.Model):
	"""Modelo para almacenar los materiales del producto partida en la linea de factura"""
	
	_name = 'account.move.line.task.material'
	_order = 'account_move_line_id, sequence, id'

	#Dominio para el campo material
	@api.model
	def _get_material_id_domain(self):
		uom_categ_id = self.env.ref('uom.uom_categ_wtime').id
		return [('uom_id.category_id', '!=', uom_categ_id)]

	#Descripcion del material
	name = fields.Char(string='Descripción', required=True)
	#Campo relación con la linea de factura
	account_move_line_id = fields.Many2one(comodel_name='account.move.line', string='Linea de pedido')
	#Material
	material_id = fields.Many2one(comodel_name='product.product', string='Material', required=True, domain=_get_material_id_domain)
	#Precios Totales de para cada material
	sale_price = fields.Float(string='P.V.', digits=dp.get_precision('Product Price'), compute='_compute_price')
	cost_price = fields.Float(string='P.C.', digits=dp.get_precision('Product Price'), compute='_compute_price')
	#Precios Unitarios para cada material
	sale_price_unit = fields.Float(string='P.V.U.', digits=dp.get_precision('Product Price'))
	cost_price_unit = fields.Float(string='P.C.U.', digits=dp.get_precision('Product Price'))
	#Cantidad de cada material
	quantity = fields.Float(string='Und.', digits=dp.get_precision('Product Unit of Measure'))
	#Descuento aplicado al precio del material
	discount = fields.Float(string='Des. (%)', digits=dp.get_precision('Discount'), default=0.0)
	#Margen
	material_margin = fields.Float(string='Margen', digits='Product Price', compute='_compute_price')
	material_margin_percent = fields.Float(string='Margen (%)', digits='Product Price', compute='_compute_price')

	sequence = fields.Integer()

	#Carga de los valores en la linea del material seleccionado
	@api.onchange('material_id')
	def _onchange_material_id(self):
		for record in self:
			record.sale_price_unit = record.material_id.list_price
			record.cost_price_unit = record.material_id.standard_price
			record.name = record.material_id.name

	#Calculo de los precios de venta y coste totales por linea de los materiales
	
	@api.depends('quantity','sale_price_unit','cost_price_unit', 'discount')
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

	