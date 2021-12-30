# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_is_zero, float_compare

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	"""docstring for SaleOrder"""
	_inherit='sale.order'

	#Precio totales, unitarios y beneficio de Trabajos Reales
	total_sp_work = fields.Float(string='P.V. Total', digits='Product Price', compute='_compute_price_work')
	total_cp_work = fields.Float(string='P.C. Total', digits='Product Price', compute='_compute_price_work')
	sale_price_work_hour = fields.Float(string='P.V. Hora', digits='Product Price', compute="_compute_price_work")
	cost_price_work_hour = fields.Float(string='P.C. Hora', digits='Product Price', compute="_compute_price_work")
	benefit_work = fields.Float(string='Beneficio', digits='Product Price', compute='_compute_price_work')
	total_hours = fields.Float(string='Total horas', compute='_compute_price_work')

	#Precio totales, unitarios y beneficio de Trabajos Presupuesto
	total_sp_ideal_work = fields.Float(string='P.V. Total', digits='Product Price', compute='_compute_price_work_ideal')
	total_cp_ideal_work = fields.Float(string='P.C. Total', digits='Product Price', compute='_compute_price_work_ideal')
	sale_price_ideal_work_hour = fields.Float(string='P.V. Hora', digits='Product Price')
	cost_price_ideal_work_hour = fields.Float(string='P.C. Hora', digits='Product Price')
	benefit_ideal_work = fields.Float(string='Beneficio', digits='Product Price', compute='_compute_price_work_ideal')
	total_ideal_hours = fields.Float(string='Total horas')
	
	#Margenes y descuento de los totales
	discount_ideal = fields.Float(string='Descuento', digits='Product Price')
	margin_real_monetary = fields.Float(string='Margen Real', digits='Product Price', compute='_compute_real')
	margin_real_percent = fields.Float(string='Margen Real', digits='Product Price', compute='_compute_real')
	margin_ideal_monetary = fields.Float(string='Margen Ideal', digits='Product Price', compute='_compute_ideal')
	margin_ideal_percent = fields.Float(string='Margen Ideal', digits='Product Price', compute='_compute_ideal')

	#Precios totales y beneficio de Materiales Presupuesto
	total_sp_material = fields.Float(string='P.V. Total', digits='Product Price', compute='_compute_price_material')
	total_cp_material = fields.Float(string='P.C. Total', digits='Product Price', compute='_compute_price_material')
	benefit_material = fields.Float(string='Beneficio', digits='Product Price', compute='_compute_price_material')

	#Precios totales y beneficio de Materiales Reales
	total_sp_real_material = fields.Float(string='P.V. Total', digits=dp.get_precision('Product Price'), compute='_compute_price_material_real')
	total_cp_real_material = fields.Float(string='P.C. Total', digits=dp.get_precision('Product Price'))
	benefit_real_material = fields.Float(string='Beneficio', digits=dp.get_precision('Product Price'), compute='_compute_price_material_real')

	#Numero de cliente
	ref = fields.Char(related='partner_id.ref', readonly=True, string='Nº. Cliente')

	#Lista de materiales usados en los compuestos
	materials_ids = fields.One2many(comodel_name='sale.order.task.material',  inverse_name='order_id', string='Materiales')
	#Lista de trabajos usados en los compuestos
	works_ids = fields.One2many(comodel_name='sale.order.task.work',  inverse_name='order_id', string='Trabajos')

	#Calculo de la lista de materiales
	
	@api.onchange('order_line', 'order_line.task_materials_ids','order_line.task_works_ids')
	def _onchange_material_ids(self):
		material_list = []
		work_list = []
		for order in self:
			for line in order.order_line:
				if line.auto_create_task:
					for material in line.task_materials_ids:
						if not material_list:
							material_list.append((0,0, {
									'order_id' : material.order_line_id.order_id.id,
									'material_id' : material.material_id.id,
									'name' : material.name,
									'sale_price_unit' : material.sale_price_unit,
									'cost_price_unit' : material.cost_price_unit,
									'quantity' : material.quantity * line.product_uom_qty,
									'discount' : material.discount,
								}))
						else: 
							encontrado = False
							for item in material_list:
								material_id = item[2]["material_id"]
								_logger.debug('List: %s ; Material: %s', material_id, material.material_id)
								if material_id == material.material_id.id:
									item[2]["quantity"] = item[2]["quantity"] + (material.quantity * line.product_uom_qty)
									encontrado = True
							if not encontrado:	
								material_list.append((0,0, {
									'order_id' : material.order_line_id.order_id.id,
									'material_id' : material.material_id.id,
									'name' : material.name,
									'sale_price_unit' : material.sale_price_unit,
									'cost_price_unit' : material.cost_price_unit,
									'quantity' : material.quantity * line.product_uom_qty,
									'discount' : material.discount,
								}))

					for work in line.task_works_ids:
						if not work_list:
							work_list.append((0,0, {
									'order_id' : work.order_line_id.order_id.id,
									'work_id' : work.work_id.id,
									'name' : work.name,
									'sale_price_unit' : work.sale_price_unit,
									'cost_price_unit' : work.cost_price_unit,
									'hours' : work.hours * line.product_uom_qty,
									'discount' : work.discount,
								}))
						else: 
							encontrado = False
							for item in work_list:
								work_id = item[2]["work_id"]
								if work_id == work.work_id.id:
									item[2]["hours"] = item[2]["hours"] + (work.hours * line.product_uom_qty)
									encontrado = True
							if not encontrado:	
								work_list.append((0,0, {
									'order_id' : work.order_line_id.order_id.id,
									'work_id' : work.work_id.id,
									'name' : work.name,
									'sale_price_unit' : work.sale_price_unit,
									'cost_price_unit' : work.cost_price_unit,
									'hours' : work.hours * line.product_uom_qty,
									'discount' : work.discount,
								}))

			order.update({'materials_ids' : material_list,
						'works_ids' : work_list})

	#Calculo de los margenes reales
	
	@api.depends('order_line')
	def _compute_real(self):
		sale = 0.0
		cost = 0.0
		self.margin_real_percent = 0.0
		for line in self.order_line:
			if line.product_id.type == 'service':
				if line.auto_create_task:
					sale = sale + ((sum(line.task_materials_ids.mapped('sale_price')) + sum(line.task_works_ids.mapped('sale_price'))) 
						* line.product_uom_qty * (1 - (line.discount/100)))
					cost = cost + ((sum(line.task_materials_ids.mapped('cost_price')) + sum(line.task_works_ids.mapped('cost_price'))) * line.product_uom_qty)
			else:
				sale = sale + (line.price_unit * line.product_uom_qty * (1 - (line.discount/100)))
				cost = cost + (line.purchase_price * line.product_uom_qty)

		self.margin_real_monetary = sale - cost
		if (cost != 0) and (sale != 0):
			self.margin_real_percent = (1-(cost/sale)) * 100

	#Calculo de los margenes ideales
	
	@api.depends('sale_price_ideal_work_hour','cost_price_ideal_work_hour','total_ideal_hours','order_line','discount_ideal','total_cp_real_material')
	def _compute_ideal(self):
		sale = 0.0
		cost = 0.0
		self.margin_ideal_percent = 0.0
		for line in self.order_line:
			if line.product_id.type == 'service':
				if line.auto_create_task:
					sale = sale + (sum(line.task_materials_ids.mapped('sale_price')) * line.product_uom_qty * (1 - (line.discount/100)))
					#cost = cost + (sum(line.task_materials_ids.mapped('cost_price')) * line.product_uom_qty)
			else:
				sale = sale + (line.price_unit * line.product_uom_qty * (1 - (line.discount/100)))
				#cost = cost + (line.purchase_price * line.product_uom_qty)

		for record in self:
			#sale = sale + (record.total_ideal_hours * record.sale_price_ideal_work_hour)
			sale = sale + record.total_sp_ideal_work
			cost = record.total_cp_real_material + (record.total_ideal_hours * record.cost_price_ideal_work_hour)
				
		sale = sale - (sale * (self.discount_ideal / 100))
		self.margin_ideal_monetary = sale - cost
		if (cost != 0) and (sale != 0):
			self.margin_ideal_percent = (1-(cost/sale)) * 100

	#Calculo del precio de venta y coste total de los materiales y su beneficio según presupuesto
	
	@api.depends('order_line')
	def _compute_price_material(self):
		sale = 0.0
		cost = 0.0
		self.benefit_material = 0.0
		for order in self:
			for line in order.order_line:
				if line.product_id.type == 'service':
					if line.auto_create_task:
						sale = sale + sum(line.task_materials_ids.mapped('sale_price')) * (line.product_uom_qty * (1 - (line.discount/100)))
						cost = cost + sum(line.task_materials_ids.mapped('cost_price')) * line.product_uom_qty
				else:
					sale = sale + ((line.price_unit * line.product_uom_qty) * (1 - (line.discount/100)))
					cost = cost + (line.purchase_price * line.product_uom_qty)
			order.total_sp_material = sale
			order.total_cp_material = cost
			if (cost != 0) and (sale != 0):
				order.benefit_material = (1-(cost/sale)) * 100

	#Calculo del precio de venta y coste total de los materiales y su beneficio reales
	@api.depends('order_line')
	def _compute_price_material_real(self):
		sale = 0.0
		cost = self.total_cp_real_material
		for line in self.order_line:
			if line.product_id.type == 'service':
				if line.auto_create_task:
					sale = sale + sum(line.task_materials_ids.mapped('sale_price')) * (line.product_uom_qty * (1 - (line.discount/100)))
			else:
				sale = sale + ((line.price_unit * line.product_uom_qty) * (1 - (line.discount/100)))
		self.total_sp_real_material = sale
		if (cost != 0) and (sale != 0):
			self.benefit_real_material = (1-(cost/sale)) * 100

	#Calculo del coste total real de los materiales
	@api.onchange('order_line')
	def _onchange_total_cp_real_material(self):
		cost = 0.0
		for line in self.order_line:
			if line.product_id.type == 'service':
				if line.auto_create_task:
					cost = cost + sum(line.task_materials_ids.mapped('cost_price')) * line.product_uom_qty
			else:
				cost = cost + (line.purchase_price * line.product_uom_qty)

		self.total_cp_real_material = cost

	#Calculo del precio de venta y coste de los trabajos y su beneficio reales
	
	@api.depends('order_line')
	def _compute_price_work(self):
		sale = 0.0
		cost = 0.0
		hours = 0.0
		self.sale_price_work_hour = 0.0
		self.cost_price_work_hour = 0.0
		self.benefit_work = 0.0
		for order in self:
			for line in order.order_line:
				if line.product_id.type == 'service':
					if line.auto_create_task:
						sale = sale + sum(line.task_works_ids.mapped('sale_price')) * (line.product_uom_qty * (1 - (line.discount/100)))
						cost = cost + sum(line.task_works_ids.mapped('cost_price')) * line.product_uom_qty
						hours = hours + sum(line.task_works_ids.mapped('hours')) * line.product_uom_qty
					else:
						sale = sale + ((line.price_unit * line.product_uom_qty) * (1 - (line.discount/100)))
						cost = cost + (line.purchase_price * line.product_uom_qty)
						hours = hours + line.product_uom_qty
			order.total_sp_work = sale
			order.total_cp_work = cost
			order.total_hours = hours
			if (hours != 0):
				order.sale_price_work_hour = sale/hours
				order.cost_price_work_hour = cost/hours
			if (cost != 0) and (sale != 0):
				order.benefit_work = (1-(cost/sale)) * 100

	#Recalcula los totales ideales al cambiar las horas
	
	@api.onchange('total_hours')
	def _onchange_total_ideal(self):
		for record in self:
			record.total_ideal_hours = record.total_hours
			#record.sale_price_ideal_work_hour = record.sale_price_work_hour
			record.cost_price_ideal_work_hour = record.cost_price_work_hour

	#Calculo del precio de venta y coste de los trabajos y su beneficio según presupuesto
	
	@api.depends('sale_price_ideal_work_hour','cost_price_ideal_work_hour','total_ideal_hours')
	def _compute_price_work_ideal(self):
		self.sale_price_ideal_work_hour = 0.0
		self.total_sp_ideal_work = 0.0
		self.total_cp_ideal_work = 0.0
		self.benefit_ideal_work = 0.0
		for record in self:
			record.sale_price_ideal_work_hour = record.sale_price_work_hour
			#record.total_sp_ideal_work = record.total_ideal_hours * record.sale_price_ideal_work_hour
			record.total_sp_ideal_work = record.total_sp_work
			record.total_cp_ideal_work = record.total_ideal_hours * record.cost_price_ideal_work_hour
			if (record.total_cp_ideal_work != 0) and (record.total_sp_ideal_work != 0):
				record.benefit_ideal_work = (1-(record.total_cp_ideal_work/record.total_sp_ideal_work)) * 100


	#Añadimos al origen las tareas asociadas al presupuesto
	"""
	def _prepare_invoice(self):
		invoice_vals = super(SaleOrder, self)._prepare_invoice()

		origin = self.name
		if self.tasks_ids:
			for line in self.tasks_ids:
				origin = origin + ", " + line.code

		invoice_vals.update({'invoice_origin': origin})

		return invoice_vals
	"""

	#Redefinimos la acción cancelar como la original
	"""
	def action_cancel(self):
		return self.write({'state': 'cancel'})"""
		
class SaleOrderTaskMaterial(models.Model):
	"""Modelo para almacenar los materiales de los productos partida en el pedido"""
	
	_name = 'sale.order.task.material'
	_order = 'order_id, material_id'

	#Descripcion del material
	name = fields.Char(string='Descripción')
	#Campo relación con el pedido
	order_id = fields.Many2one(comodel_name='sale.order', string='Pedido')
	#Material
	material_id = fields.Many2one(comodel_name='product.product', string='Material', required=True)
	#Precios Totales de para cada material
	sale_price = fields.Float(string='Precio Venta', digits='Product Price', compute='_compute_price')
	cost_price = fields.Float(string='Precio Coste', digits='Product Price', compute='_compute_price')
	#Precios Unitarios para cada material
	sale_price_unit = fields.Float(string='P.V. unitario', digits='Product Price')
	cost_price_unit = fields.Float(string='P.C. unitario', digits='Product Price')
	#Cantidad de cada material
	quantity = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'))
	#Descuento aplicado al precio del material
	discount = fields.Float(string='Descuento (%)', digits=dp.get_precision('Discount'), default=0.0)
	sequence = fields.Integer()
	
	#Calculo de los precios de venta y coste totales por linea de los materiales
	
	@api.depends('quantity','sale_price_unit','cost_price_unit','discount')
	def _compute_price(self):
		self.sale_price = 0.0
		self.cost_price = 0.0
		for record in self:
				record.sale_price = record.quantity * (record.sale_price_unit * (1 - (record.discount / 100)))
				record.cost_price = (record.quantity * record.cost_price_unit)

class SaleOrderTaskWork(models.Model):
	"""Modelo para almacenar los trabajos del producto partida en la linea de pedido"""

	_name = 'sale.order.task.work'
	_order = 'order_id, work_id'

	#Campo relación con el pedido
	order_id = fields.Many2one(comodel_name='sale.order', string='Pedido')
	#Mano de obra
	work_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', required=True)
	#Descripcion del trabajo
	name = fields.Char(string='Nombre')
	#Precios Totales para cada trabajo
	sale_price = fields.Float(string='Precio Venta', digits='Product Price', compute="_compute_price")
	cost_price = fields.Float(string='Precio Coste', digits='Product Price', compute="_compute_price")
	#Precios Unitarios para cada trabajo
	sale_price_unit = fields.Float(string='P.V. unitario', digits='Product Price')
	cost_price_unit = fields.Float(string='P.C. unitario', digits='Product Price')
	#Horas empleadas en el trabajo
	hours = fields.Float(string='Horas')
	#Descuento aplicado al precio de la mano de obra
	discount = fields.Float(string='Descuento (%)', digits=dp.get_precision('Discount'), default=0.0)
	sequence = fields.Integer()

	#Calculo de los precios de venta y coste totales por linea de los trabajos
	
	@api.depends('hours','sale_price_unit', 'cost_price_unit', 'discount')
	def _compute_price(self):
		self.sale_price = 0.0
		self.cost_price = 0.0
		for record in self:
			record.sale_price = record.hours * (record.sale_price_unit * (1 - (record.discount / 100)))
			record.cost_price = (record.hours * record.cost_price_unit)

class SaleOrderLine(models.Model):

	_inherit='sale.order.line'

	#Campos relacionales para trabajos y materiales
	task_works_ids = fields.One2many(comodel_name='sale.order.line.task.work', inverse_name='order_line_id', string='Trabajos', copy=True)
	task_materials_ids = fields.One2many(comodel_name='sale.order.line.task.material', inverse_name='order_line_id', string='Materiales', copy=True)
	#Precio totales, unitarios y beneficio de Trabajos
	total_sp_work = fields.Float(string='Total P.V.', digits='Product Price', compute='_compute_total_sp_work')
	total_cp_work = fields.Float(string='Total P.C.', digits='Product Price', compute='_compute_total_cp_work')
	benefit_work = fields.Float(string='Beneficio', digits='Product Price', compute='_compute_benefit_work')
	total_hours = fields.Float(string='Total horas', compute='_compute_total_hours')
	#Precios totales, unitarios  y beneficio de Materiales
	total_sp_material = fields.Float(string='Total P.V.', digits='Product Price', compute='_compute_total_sp_material')
	total_cp_material = fields.Float(string='Total P.C.', digits='Product Price', compute='_compute_total_cp_material')
	benefit_material = fields.Float(string='Beneficio', digits='Product Price', compute='_compute_benefit_material')
	#Campo boolean para saber si crear o no una tarea de forma automatica
	auto_create_task = fields.Boolean(string='Tarea automática', copy=True)
	#Opciones de impresión por linea de pedido
	detailed_time = fields.Boolean(string='Imp. horas')
	detailed_price_time = fields.Boolean(string='Imp. precio Hr.')
	detailed_materials = fields.Boolean(string='Imp.materiales')
	detailed_price_materials = fields.Boolean(string='Imp. precio Mat.')
	detailed_subtotal_price_time = fields.Boolean(string='Imp. subtotal Hr.')
	detailed_subtotal_price_materials = fields.Boolean(string='Imp. subtotal Mat.')

	#Albaranes relacionados
	#picking_ids = fields.One2many('stock.picking', string='Albaranes', compute='_compute_picking_ids')

	#Albaranes relacionados con la linea de pedido
	"""
	@api.depends('move_ids')
	def _compute_picking_ids(self):
		for line in self:
			line.picking_ids = line.mapped('move_ids.picking_id')
	"""

	#Estado de la factura de una linea de pedido
	def _compute_invoice_status(self):
		super(SaleOrderLine, self)._compute_invoice_status()
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		for line in self:
			if line.state not in ('sale', 'done'):
				line.invoice_status = 'no'
			elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
				line.invoice_status = 'to invoice'
			elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
				line.invoice_status = 'invoiced'
			else:
				line.invoice_status = 'no'

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
		for record in self:
			if (record.total_sp_work != 0) and (record.total_cp_work != 0):
				record.benefit_work = (1-(record.total_cp_work/record.total_sp_work)) * 100

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
		for record in self:
			if (record.total_cp_material != 0) and (record.total_sp_material != 0):
				record.benefit_material = (1-(record.total_cp_material/record.total_sp_material)) * 100

	#Obtiene el precio del material o mano de obra segun tarifa
	
	def _get_display_price_line(self, product, product_id, quantity):
		
		no_variant_attributes_price_extra = [
			ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
				lambda ptav:
					ptav.price_extra and
					ptav not in product.product_template_attribute_value_ids
			)
		]
		if no_variant_attributes_price_extra:
			product = product.with_context(
				no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
			)


		if self.order_id.pricelist_id.discount_policy == 'with_discount':
			return product.with_context(pricelist=self.order_id.pricelist_id.id).price

		product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=product_id.uom_id.id)
		final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product_id, quantity or 1.0, self.order_id.partner_id)
		base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, quantity, product_id.uom_id, self.order_id.pricelist_id.id)

		if currency != self.order_id.pricelist_id.currency_id:
			base_price = currency._convert(
				base_price, self.order_id.pricelist_id.currency_id,
				self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())

		return max(base_price, final_price)

	#Calculo del descuento según la tarifa
	
	def _get_discount_line(self, product_id, quantity):
		if not (product_id and product_id.uom_id and 
				self.order_id.partner_id and 
				self.order_id.pricelist_id and 
				self.order_id.pricelist_id.discount_policy == 'without_discount' and 
				self.env.user.has_group('product.group_discount_per_so_line')):
			return

		product = product_id.with_context(
			lang=self.order_id.partner_id.lang,
			partner=self.order_id.partner_id.id,
			quantity=quantity,
			date=self.order_id.date_order,
			pricelist=self.order_id.pricelist_id.id,
			uom=product_id.uom_id.id,
			fiscal_position=self.env.context.get('fiscal_position'))

		product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=product_id.uom_id.id)

		price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product_id, quantity or 1.0, self.order_id.partner_id)
		new_list_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, quantity, product_id.uom_id, self.order_id.pricelist_id.id)

		if new_list_price != 0:
			if self.order_id.pricelist_id.currency_id != currency:
				#necesitamos que new_list_price este en la misma moneda que price, 
				#la cual esta en la moneda de la tarida del presupuesto
				new_list_price = currency._convert(
					new_list_price, self.order_id.pricelist_id.currency_id,
					self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
			
			discount = (new_list_price - price) / new_list_price * 100
			if (discount > 0):
				return discount

	#Carga de los datos del producto en la linea de pedido al seleccionar dicho producto
	
	@api.onchange('product_id')
	def product_id_change(self):
		result = super(SaleOrderLine, self).product_id_change()
		product = self.product_id
		if product:
			self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_in_project')

		if self.auto_create_task:
			work_list = []
			for work in product.task_works_ids:
				workforce = work.work_id.with_context(
					lang=self.order_id.partner_id.lang,
					partner=self.order_id.partner_id.id,
					quantity=work.hours,
					date=self.order_id.date_order,
					pricelist=self.order_id.pricelist_id.id,
					uom=work.work_id.uom_id.id)

				work_list.append((0,0, {
					'name' : work.name,
					'work_id': work.work_id.id,
					'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(workforce, work.work_id, work.hours), workforce.taxes_id, self.tax_id, self.company_id),
					'cost_price_unit' : work.cost_price_unit,
					'hours' : work.hours,
					'discount' : self._get_discount_line(work.work_id, work.hours) or 0.0
					}))

			material_list = []
			for material in product.task_materials_ids:
				mat = material.material_id.with_context(
						lang=self.order_id.partner_id.lang,
						partner=self.order_id.partner_id.id,
						quantity=material.quantity,
						date=self.order_id.date_order,
						pricelist=self.order_id.pricelist_id.id,
						uom=material.material_id.uom_id.id)

				material_list.append((0,0, {
					'material_id' : material.material_id.id,
					'name' : material.name,
					'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(mat, material.material_id, material.quantity), mat.taxes_id, self.tax_id, self.company_id),
					'cost_price_unit' : material.cost_price_unit,
					'quantity' : material.quantity,
					'discount' : self._get_discount_line(material.material_id, material.quantity) or 0.0
					}))

			self.update({'task_works_ids' : work_list,
					'task_materials_ids' : material_list,
					'auto_create_task' : True})

			#for line in self:
			#	line.price_unit = (line.total_sp_material + line.total_sp_work)

		else:
			self.update({'task_works_ids' : False,
					'task_materials_ids' : False,
					'auto_create_task' : False})
		return result

	#Calculo del precio de venta y coste del prodcuto tipo partida en la linea de pedido
	#al producirse algun cambio en los materiales, trabajos o mano de obra
	
	@api.onchange('task_materials_ids', 'task_works_ids')
	def _onchange_task_materials_works_workforce(self):
		product = self.product_id
		if product:
			self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_in_project')
		else:
			self.price_unit = 0.0
			return
			
		if self.auto_create_task and self.order_id.pricelist_id and self.order_id.partner_id:
			for line in self:
				#Guardamos los precios de la ficha de producto
				product_lst_price = line.product_id.lst_price
				product_standard_price = line.product_id.standard_price

				#Actualizamos los precios de la ficha de producto con los precios de la linea de pedido
				line.product_id.write({
					'lst_price' : (line.total_sp_material + line.total_sp_work),
					'standard_price' : (line.total_cp_material + line.total_cp_work),
				})

				#Aplicamos la tarifa
				product = line.product_id.with_context(
					lang=line.order_id.partner_id.lang,
					partner=line.order_id.partner_id.id,
					quantity=line.product_uom_qty,
					date=line.order_id.date_order,
					pricelist=line.order_id.pricelist_id.id,
					uom=line.product_uom.id,
					fiscal_position=self.env.context.get('fiscal_position')
				)

				if line.product_id.apply_pricelist:
					line.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
				else:
					line.price_unit = line.total_sp_material + line.total_sp_work
				line.purchase_price = (line.total_cp_material + line.total_cp_work)

				#Recuperamos los precios de la ficha producto previamente guardado
				line.product_id.write({
					'lst_price' : product_lst_price,
					'standard_price' : product_standard_price,
				})
			

	#Cuando se cambie la cantida o las unidades del producto aplique la tarifa a los trabajos y
	#materiales si es de tipo partida el producto
	@api.onchange('product_uom', 'product_uom_qty')
	def product_uom_change(self):
		result = super(SaleOrderLine, self).product_uom_change()
		product = self.product_id
		if product:
			self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_in_project')

		if self.auto_create_task and self.order_id.pricelist_id and self.order_id.partner_id:
			for line in self:
				#Guardamos los precios de la ficha de producto
				product_lst_price = line.product_id.lst_price
				product_standard_price = line.product_id.standard_price

				#Actualizamos los precios de la ficha de producto con los precios de la linea de pedido
				line.product_id.write({
					'lst_price' : (line.total_sp_material + line.total_sp_work),
					'standard_price' : (line.total_cp_material + line.total_cp_work),
				})

				#Aplicamos la tarifa
				product = line.product_id.with_context(
					lang=line.order_id.partner_id.lang,
					partner=line.order_id.partner_id.id,
					quantity=line.product_uom_qty,
					date=line.order_id.date_order,
					pricelist=line.order_id.pricelist_id.id,
					uom=line.product_uom.id,
					fiscal_position=self.env.context.get('fiscal_position')
				)
				if line.product_id.apply_pricelist:
					line.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
				else:
					line.price_unit = line.total_sp_material + line.total_sp_work
				line.purchase_price = (line.total_cp_material + line.total_cp_work)

				#Recuperamos los precios de la ficha producto previamente guardado
				line.product_id.write({
					'lst_price' : product_lst_price,
					'standard_price' : product_standard_price,
				})

		return result

	#Calculo de las horas estimadas al crear el parte de trabajo correspondiente a la linea de pedido
	def _convert_qty_company_hours(self,dest_company):
		company_time_uom_id = dest_company.project_time_mode_id
		if self.product_uom.id != company_time_uom_id.id and self.product_uom.category_id.id == company_time_uom_id.category_id.id:
			planned_hours = self.product_uom._compute_quantity(self.product_uom_qty, company_time_uom_id)
		else:
			planned_hours = sum(self.task_works_ids.mapped('hours')) * self.product_uom_qty
		return planned_hours
	
	#Creación del proyecto
	"""
	def _timesheet_find_project(self):
		self.ensure_one()
		Project = self.env['project.project']
		project = self.product_id.with_context(
			force_company=self.company_id.id).project_id
		if not project:
			# find the project corresponding to the analytic account of the sales order
			account = self.order_id.analytic_account_id
			if not account:
				self.order_id._create_analytic_account(
					prefix=self.order_id.opportunity_id.name or None)
				account = self.order_id.analytic_account_id
			project = Project.search(
				[('analytic_account_id', '=', account.id)], limit=1)
			if not project:
				project_name = '%s (%s)' % (
					account.name, self.order_partner_id.ref) if self.order_partner_id.ref else account.name
				project = Project.create({
					'name': project_name,
					'allow_timesheets': self.product_id.service_type == 'timesheet',
					'analytic_account_id': account.id,
				})
				# set the SO line origin if product should create project
				if not project.sale_line_id and self.product_id.service_tracking in ['task_in_project', 'project_only']:
					project.write({'sale_line_id': self.id})
		return project
	"""

	#Calculo de los valores necesarios para crear el parte de trabajo correspondiente a la linea de pedido
	def _timesheet_create_task_prepare_values(self, project):
		self.ensure_one()
		planned_hours = self._convert_qty_company_hours(self.company_id)
		sale_line_name_parts = self.name.split('\n')
		title = sale_line_name_parts[0] or self.product_id.name
		work_list = []
		for work in self.task_works_ids:
			work_list.append((0,0, {
				'work_id' : work.work_id.id,
				'name' : work.name,
				'hours' : work.hours * self.product_uom_qty,
				}))

		material_list = []
		for material in self.task_materials_ids:
			material_list.append((0,0, {
				'product_id' : material.material_id.id,
				'quantity' : material.quantity * self.product_uom_qty,
				}))

		return {
			'name': title if project.sale_line_id else '%s: %s' % (self.order_id.name or '', title),
			'planned_hours': planned_hours,
			'remaining_hours': planned_hours,
			'partner_id': self.order_id.partner_id.id,
			'description': self.name + '<br/>',
			'work_to_do' : self.name + '<br/>',
			'project_id': project.id,
			'sale_line_id': self.id,
			'company_id': project.company_id.id,
			'email_from': self.order_id.partner_id.email,
			'user_id': False, # force non assigned task, as created as sudo()
			'material_ids': material_list,
			'task_works_ids': work_list,
			'oppor_id': self.order_id.opportunity_id.id or False, # Asocia con el aviso
			}

	#Calculo de los valores necesarios de la linea factura asociada a la linea de pedido, al crear la factura del pedido
	
	def _prepare_invoice_line(self, **optional_values):
		res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)

		"""origin = self.order_id.name
		if self.task_ids:
			for line in self.task_ids:
				origin = origin + ", " + line.code

		res.update({'invoice_origin': origin})"""

		work_list = []
		material_list = []
		if res:
			if self.task_works_ids:
				for work in self.task_works_ids:
					workforce = work.work_id.with_context(
					lang=self.order_id.partner_id.lang,
					partner=self.order_id.partner_id.id,
					quantity=work.hours,
					date=self.order_id.date_order,
					pricelist=self.order_id.pricelist_id.id,
					uom=work.work_id.uom_id.id)

					work_list.append((0,0, {
						'name' : work.name,
						'work_id': work.work_id.id,
						'sale_price_unit' : work.sale_price_unit,
						#'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(workforce, work.work_id, work.hours), workforce.taxes_id, self.tax_id, self.company_id),
						'cost_price_unit' : work.cost_price_unit,
						'hours' : work.hours,
						'discount' : self._get_discount_line(work.work_id, work.hours) or 0.0
					}))
			else:
				work_list = False

			if self.task_materials_ids:
				for material in self.task_materials_ids:
					mat = material.material_id.with_context(
					lang=self.order_id.partner_id.lang,
					partner=self.order_id.partner_id.id,
					quantity=material.quantity,
					date=self.order_id.date_order,
					pricelist=self.order_id.pricelist_id.id,
					uom=material.material_id.uom_id.id)

					material_list.append((0,0, {
						'material_id' : material.material_id.id,
						'name' : material.name,
						'sale_price_unit' : material.sale_price_unit,
						#'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(mat, material.material_id, material.quantity), mat.taxes_id, self.tax_id, self.company_id),
						'cost_price_unit' : material.cost_price_unit,
						'quantity' : material.quantity,
						'discount' : self._get_discount_line(material.material_id, material.quantity) or 0.0
					}))
			else:
				material_list = False

			res.update({'task_works_ids' : work_list,
					'task_materials_ids' : material_list})

			res['auto_create_task'] = self.auto_create_task
			res['detailed_time'] = self.detailed_time
			res['detailed_price_time'] = self.detailed_price_time
			res['detailed_materials'] = self.detailed_materials
			res['detailed_price_materials'] = self.detailed_price_materials
			res['detailed_subtotal_price_time'] = self.detailed_subtotal_price_time
			res['detailed_subtotal_price_materials'] = self.detailed_subtotal_price_materials

		return res

	"""
	def action_view_task(self):
		self.ensure_one()
		action = self.env.ref('project.action_view_task')
		form_view_id = self.env.ref('project.view_task_form2').id

		result = {
			'name': action.name,
			'help': action.help,
			'type': action.type,
			'views': [[False, 'kanban'], [False, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'calendar'], [False, 'pivot'], [False, 'graph']],
			'target': action.target,
			'context': "{'group_by':'stage_id'}",
			'res_model': action.res_model,
			
		}
		if len(self.task_id) == 1:
			result['views'] = [(form_view_id, 'form')]
			result['res_id'] = self.task_id.id
		else:
			result = {'type': 'ir.actions.act_window_close'}
		return result"""


class SaleOrderLineTaskWork(models.Model):
	"""Modelo para almacenar los trabajos del producto partida en la linea de pedido"""

	_name = 'sale.order.line.task.work'
	_order = 'order_line_id, sequence, id'

	#Campo relación con la linea de pedido
	order_line_id = fields.Many2one(comodel_name='sale.order.line', string='Linea de pedido')
	#Mano de obra
	work_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', required=True)
	#Descripcion del trabajo
	name = fields.Char(string='Nombre', required=True)
	#Precios Totales para cada trabajo
	sale_price = fields.Float(string='Precio Venta', digits='Product Price', compute="_compute_price")
	cost_price = fields.Float(string='Precio Coste', digits='Product Price', compute="_compute_price")
	#Precios Unitarios para cada trabajo
	sale_price_unit = fields.Float(string='P.V. unitario', digits='Product Price')
	cost_price_unit = fields.Float(string='P.C. unitario', digits='Product Price')
	#Horas empleadas en el trabajo
	hours = fields.Float(string='Horas')
	#Descuento aplicado al precio de la mano de obra
	discount = fields.Float(string='Descuento (%)', digits=dp.get_precision('Discount'), default=0.0)
	sequence = fields.Integer()

	#Obtiene el precio de la mano de obra segun tarifa
	
	def _get_display_price_workforce(self, workforce):
		if self.order_line_id.order_id.pricelist_id.discount_policy == 'with_discount':
			return workforce.with_context(pricelist=self.order_line_id.order_id.pricelist_id.id).price

		workforce_context = dict(self.env.context, partner_id=self.order_line_id.order_id.partner_id.id, date=self.order_line_id.order_id.date_order, uom=self.work_id.uom_id.id)
		final_price, rule_id = self.order_line_id.order_id.pricelist_id.with_context(workforce_context).get_product_price_rule(self.work_id, self.hours or 1.0, self.order_line_id.order_id.partner_id)
		base_price, currency = self.order_line_id.with_context(workforce_context)._get_real_price_currency(workforce, rule_id, self.hours, self.work_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		if currency != self.order_line_id.order_id.pricelist_id.currency_id:
			base_price = currency._convert(
				base_price, self.order_line_id.order_id.pricelist_id.currency_id,
				self.order_line_id.order_id.company_id or self.env.company, self.order_line_id.order_id.date_order or fields.Date.today())

		return max(base_price, final_price)

	#Calculo del precio de venta y coste unitario segun tarifa al cambiar las horas
	
	@api.onchange('hours')
	def _onchange_hours(self):
		for record in self:
			if record.work_id:
				workforce = record.work_id.with_context(
					lang=record.order_line_id.order_id.partner_id.lang,
					partner=record.order_line_id.order_id.partner_id.id,
					quantity=record.hours,
					date=record.order_line_id.order_id.date_order,
					pricelist=record.order_line_id.order_id.pricelist_id.id,
					uom=record.work_id.uom_id.id)

				record.sale_price_unit = record.order_line_id.env['account.tax']._fix_tax_included_price_company(self._get_display_price_workforce(workforce), workforce.taxes_id, self.order_line_id.tax_id, self.order_line_id.company_id)
				record.cost_price_unit = record.work_id.standard_price
				record.name = record.work_id.name
	
	#Carga de los valores en la linea de la mano de obra seleccionada
	
	@api.onchange('work_id')
	def _onchange_work_id(self):
		for record in self:
			if record.work_id:
				workforce = record.work_id.with_context(
					lang=record.order_line_id.order_id.partner_id.lang,
					partner=record.order_line_id.order_id.partner_id.id,
					quantity=record.hours,
					date=record.order_line_id.order_id.date_order,
					pricelist=record.order_line_id.order_id.pricelist_id.id,
					uom=record.work_id.uom_id.id)

				record.sale_price_unit = record.order_line_id.env['account.tax']._fix_tax_included_price_company(self._get_display_price_workforce(workforce), workforce.taxes_id, self.order_line_id.tax_id, self.order_line_id.company_id)
				record.cost_price_unit = record.work_id.standard_price
				record.name = record.work_id.name

	#Calculo del descuento según la tarifa
	@api.onchange('work_id','hours')
	def _onchange_discount(self):
		if not (self.work_id and self.work_id.uom_id and 
				self.order_line_id.order_id.partner_id and 
				self.order_line_id.order_id.pricelist_id and 
				self.order_line_id.order_id.pricelist_id.discount_policy == 'without_discount' and 
				self.env.user.has_group('product.group_discount_per_so_line')):
			return

		self.discount = 0.0
		workforce = self.work_id.with_context(
			lang=self.order_line_id.order_id.partner_id.lang,
			partner=self.order_line_id.order_id.partner_id.id,
			quantity=self.hours,
			date=self.order_line_id.order_id.date_order,
			pricelist=self.order_line_id.order_id.pricelist_id.id,
			uom=self.work_id.uom_id.id,
			fiscal_position=self.env.context.get('fiscal_position'))

		workforce_context = dict(self.env.context, partner_id=self.order_line_id.order_id.partner_id.id, date=self.order_line_id.order_id.date_order, uom=self.work_id.uom_id.id)

		price, rule_id = self.order_line_id.order_id.pricelist_id.with_context(workforce_context).get_product_price_rule(self.work_id, self.hours or 1.0, self.order_line_id.order_id.partner_id)
		new_list_price, currency = self.order_line_id.with_context(workforce_context)._get_real_price_currency(workforce, rule_id, self.hours, self.work_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		if new_list_price != 0:
			if self.order_line_id.order_id.pricelist_id.currency_id != currency:
				#necesitamos que new_list_price este en la misma moneda que price, 
				#la cual esta en la moneda de la tarida del presupuesto
				new_list_price = currency._convert(
					new_list_price, self.order_line_id.order_id.pricelist_id.currency_id,
					self.order_line_id.order_id.company_id or self.env.company, self.order_line_id.order_id.date_order or fields.Date.today())
			
			discount = (new_list_price - price) / new_list_price * 100
			if discount > 0:
				self.discount = discount

	#Calculo de los precios de venta y coste totales por linea de los trabajos
	#
	@api.depends('hours','sale_price_unit', 'cost_price_unit', 'discount')
	def _compute_price(self):
		self.sale_price = 0.0
		self.cost_price = 0.0
		for record in self:
			record.sale_price = record.hours * (record.sale_price_unit * (1 - (record.discount / 100)))
			record.cost_price = (record.hours * record.cost_price_unit)

class SaleOrderLineTaskMaterial(models.Model):
	"""Modelo para almacenar los materiales del producto partida en la linea de pedido"""
	
	_name = 'sale.order.line.task.material'
	_order = 'order_line_id, sequence, id'

	#Descripcion del material
	name = fields.Char(string='Descripción', required=True)
	#Campo relación con la linea de pedido
	order_line_id = fields.Many2one(comodel_name='sale.order.line', string='Linea de pedido')
	#Material
	material_id = fields.Many2one(comodel_name='product.product', string='Material', required=True)
	#Precios Totales de para cada material
	sale_price = fields.Float(string='Precio Venta', digits='Product Price', compute='_compute_price')
	cost_price = fields.Float(string='Precio Coste', digits='Product Price', compute='_compute_price')
	#Precios Unitarios para cada material
	sale_price_unit = fields.Float(string='P.V. unitario', digits='Product Price')
	cost_price_unit = fields.Float(string='P.C. unitario', digits='Product Price')
	#Cantidad de cada material
	quantity = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'))
	#Descuento aplicado al precio del material
	discount = fields.Float(string='Descuento (%)', digits=dp.get_precision('Discount'), default=0.0)
	sequence = fields.Integer()

	#Obtiene el precio del material segun tarifa
	
	def _get_display_price_material(self, material):
		if self.order_line_id.order_id.pricelist_id.discount_policy == 'with_discount':
			return material.with_context(pricelist=self.order_line_id.order_id.pricelist_id.id).price

		material_context = dict(self.env.context, partner_id=self.order_line_id.order_id.partner_id.id, date=self.order_line_id.order_id.date_order, uom=self.material_id.uom_id.id)
		final_price, rule_id = self.order_line_id.order_id.pricelist_id.with_context(material_context).get_product_price_rule(self.material_id, self.quantity or 1.0, self.order_line_id.order_id.partner_id)
		base_price, currency = self.order_line_id.with_context(material_context)._get_real_price_currency(material, rule_id, self.quantity, self.material_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		if currency != self.order_line_id.order_id.pricelist_id.currency_id:
			base_price = currency._convert(
				base_price, self.order_line_id.order_id.pricelist_id.currency_id,
				self.order_line_id.order_id.company_id or self.env.company, self.order_line_id.order_id.date_order or fields.Date.today())

		return max(base_price, final_price)

	#Carga de los valores en la linea del material seleccionado
	
	@api.onchange('material_id')
	def _onchange_material_id(self):
		for record in self:
			if record.material_id:
				material = record.material_id.with_context(
					lang=record.order_line_id.order_id.partner_id.lang,
					partner=record.order_line_id.order_id.partner_id.id,
					quantity=record.quantity,
					date=record.order_line_id.order_id.date_order,
					pricelist=record.order_line_id.order_id.pricelist_id.id,
					uom=record.material_id.uom_id.id)
			
				record.sale_price_unit = record.order_line_id.env['account.tax']._fix_tax_included_price_company(self._get_display_price_material(material), material.taxes_id, self.order_line_id.tax_id, self.order_line_id.company_id)
				record.cost_price_unit = record.material_id.standard_price
				record.quantity = 1.0
				record.name = record.material_id.name

	#Calculo del precio de venta y coste unitario segun tarifa al cambiar la cantidad
	
	@api.onchange('quantity')
	def _onchange_quantity(self):
		for record in self:
			if record.material_id:
				material = record.material_id.with_context(
					lang=record.order_line_id.order_id.partner_id.lang,
					partner=record.order_line_id.order_id.partner_id.id,
					quantity=record.quantity,
					date=record.order_line_id.order_id.date_order,
					pricelist=record.order_line_id.order_id.pricelist_id.id,
					uom=record.material_id.uom_id.id)
			
				record.sale_price_unit = record.order_line_id.env['account.tax']._fix_tax_included_price_company(self._get_display_price_material(material), material.taxes_id, self.order_line_id.tax_id, self.order_line_id.company_id)
				record.cost_price_unit = record.material_id.standard_price

	#Calculo del descuento según la tarifa
	@api.onchange('material_id','quantity')
	def _onchange_discount(self):
		if not (self.material_id and self.material_id.uom_id and 
				self.order_line_id.order_id.partner_id and 
				self.order_line_id.order_id.pricelist_id and 
				self.order_line_id.order_id.pricelist_id.discount_policy == 'without_discount' and 
				self.env.user.has_group('product.group_discount_per_so_line')):
			return

		self.discount = 0.0
		mat = self.material_id.with_context(
			lang=self.order_line_id.order_id.partner_id.lang,
			partner=self.order_line_id.order_id.partner_id.id,
			quantity=self.quantity,
			date=self.order_line_id.order_id.date_order,
			pricelist=self.order_line_id.order_id.pricelist_id.id,
			uom=self.material_id.uom_id.id,
			fiscal_position=self.env.context.get('fiscal_position'))

		mat_context = dict(self.env.context, partner_id=self.order_line_id.order_id.partner_id.id, date=self.order_line_id.order_id.date_order, uom=self.material_id.uom_id.id)

		price, rule_id = self.order_line_id.order_id.pricelist_id.with_context(mat_context).get_product_price_rule(self.material_id, self.quantity or 1.0, self.order_line_id.order_id.partner_id)
		new_list_price, currency = self.order_line_id.with_context(mat_context)._get_real_price_currency(mat, rule_id, self.quantity, self.material_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		if new_list_price != 0:
			if self.order_line_id.order_id.pricelist_id.currency_id != currency:
				#necesitamos que new_list_price este en la misma moneda que price, 
				#la cual esta en la moneda de la tarida del presupuesto
				new_list_price = currency._convert(
					new_list_price, self.order_line_id.order_id.pricelist_id.currency_id,
					self.order_line_id.order_id.company_id or self.env.company, self.order_line_id.order_id.date_order or fields.Date.today())
			
			discount = (new_list_price - price) / new_list_price * 100
			if discount > 0:
				self.discount = discount

	#Calculo de los precios de venta y coste totales por linea de los materiales
	#
	@api.depends('quantity','sale_price_unit','cost_price_unit','discount')
	def _compute_price(self):
		self.sale_price = 0.0
		self.cost_price = 0.0
		for record in self:
				record.sale_price = record.quantity * (record.sale_price_unit * (1 - (record.discount / 100)))
				record.cost_price = (record.quantity * record.cost_price_unit)
