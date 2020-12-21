# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp

class SaleOrder(models.Model):
	"""docstring for SaleOrder"""
	_inherit='sale.order'

	#Precio totales, unitarios y beneficio de Trabajos Reales
	total_sp_work = fields.Float(string='P.V. Total', digits=dp.get_precision('Product Price'), compute='_compute_price_work')
	total_cp_work = fields.Float(string='P.C. Total', digits=dp.get_precision('Product Price'), compute='_compute_price_work')
	sale_price_work_hour = fields.Float(string='P.V. Hora', digits=dp.get_precision('Product Price'), compute="_compute_price_work")
	cost_price_work_hour = fields.Float(string='P.C. Hora', digits=dp.get_precision('Product Price'), compute="_compute_price_work")
	benefit_work = fields.Float(string='Beneficio', digits=dp.get_precision('Product Price'), compute='_compute_price_work')
	total_hours = fields.Float(string='Total horas', compute='_compute_price_work')

	#Precio totales, unitarios y beneficio de Trabajos Ideales
	total_sp_ideal_work = fields.Float(string='P.V. Total', digits=dp.get_precision('Product Price'), compute='_compute_price_work_ideal')
	total_cp_ideal_work = fields.Float(string='P.C. Total', digits=dp.get_precision('Product Price'), compute='_compute_price_work_ideal')
	sale_price_ideal_work_hour = fields.Float(string='P.V. Hora', digits=dp.get_precision('Product Price'))
	cost_price_ideal_work_hour = fields.Float(string='P.C. Hora', digits=dp.get_precision('Product Price'))
	benefit_ideal_work = fields.Float(string='Beneficio', digits=dp.get_precision('Product Price'), compute='_compute_price_work_ideal')
	total_ideal_hours = fields.Float(string='Total horas')
	
	#Margenes y descuento de los totales
	discount_ideal = fields.Float(string='Descuento', digits=dp.get_precision('Product Price'))
	margin_real_monetary = fields.Float(string='Margen Real', digits=dp.get_precision('Product Price'), compute='_compute_real')
	margin_real_percent = fields.Float(string='Margen Real', digits=dp.get_precision('Product Price'), compute='_compute_real')
	margin_ideal_monetary = fields.Float(string='Margen Ideal', digits=dp.get_precision('Product Price'), compute='_compute_ideal')
	margin_ideal_percent = fields.Float(string='Margen Ideal', digits=dp.get_precision('Product Price'), compute='_compute_ideal')

	#Precios totales y beneficio de Materiales
	total_sp_material = fields.Float(string='P.V. Total', digits=dp.get_precision('Product Price'), compute='_compute_price_material')
	total_cp_material = fields.Float(string='P.C. Total', digits=dp.get_precision('Product Price'), compute='_compute_price_material')
	benefit_material = fields.Float(string='Beneficio', digits=dp.get_precision('Product Price'), compute='_compute_price_material')
	#Numero de cliente
	ref = fields.Char(related='partner_id.ref', readonly=True, string='Nº. Cliente')

	#Calculo de los margenes reales
	@api.multi
	@api.depends('order_line')
	def _compute_real(self):
		sale = 0.0
		cost = 0.0
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
	@api.multi
	@api.depends('sale_price_ideal_work_hour','cost_price_ideal_work_hour','total_ideal_hours','order_line','discount_ideal')
	def _compute_ideal(self):
		sale = 0.0
		cost = 0.0
		for line in self.order_line:
			if line.product_id.type == 'service':
				if line.auto_create_task:
					sale = sale + (sum(line.task_materials_ids.mapped('sale_price')) * line.product_uom_qty * (1 - (line.discount/100)))
					cost = cost + (sum(line.task_materials_ids.mapped('cost_price')) * line.product_uom_qty)
			else:
				sale = sale + (line.price_unit * line.product_uom_qty * (1 - (line.discount/100)))
				cost = cost + (line.purchase_price * line.product_uom_qty)

		for record in self:
			#sale = sale + (record.total_ideal_hours * record.sale_price_ideal_work_hour)
			sale = sale + record.total_sp_ideal_work
			cost = cost + (record.total_ideal_hours * record.cost_price_ideal_work_hour)
				
		sale = sale - (sale * (self.discount_ideal / 100))
		self.margin_ideal_monetary = sale - cost
		if (cost != 0) and (sale != 0):
			self.margin_ideal_percent = (1-(cost/sale)) * 100

	#Calculo del precio de venta y coste total de los materiales y su beneficio
	@api.multi
	@api.depends('order_line')
	def _compute_price_material(self):
		sale = 0.0
		cost = 0.0
		for line in self.order_line:
			if line.product_id.type == 'service':
				if line.auto_create_task:
					sale = sale + sum(line.task_materials_ids.mapped('sale_price')) * (line.product_uom_qty * (1 - (line.discount/100)))
					cost = cost + sum(line.task_materials_ids.mapped('cost_price')) * line.product_uom_qty
			else:
				sale = sale + ((line.price_unit * line.product_uom_qty) * (1 - (line.discount/100)))
				cost = cost + (line.purchase_price * line.product_uom_qty)
		self.total_sp_material = sale
		self.total_cp_material = cost
		if (cost != 0) and (sale != 0):
			self.benefit_material = (1-(cost/sale)) * 100

	#Calculo del precio de venta y coste de los trabajos y su beneficio
	@api.multi
	@api.depends('order_line')
	def _compute_price_work(self):
		sale = 0.0
		cost = 0.0
		hours = 0.0
		for line in self.order_line:
			if line.product_id.type == 'service':
				if line.auto_create_task:
					sale = sale + sum(line.task_works_ids.mapped('sale_price')) * (line.product_uom_qty * (1 - (line.discount/100)))
					cost = cost + sum(line.task_works_ids.mapped('cost_price')) * line.product_uom_qty
					hours = hours + sum(line.task_works_ids.mapped('hours')) * line.product_uom_qty
				else:
					sale = sale + ((line.price_unit * line.product_uom_qty) * (1 - (line.discount/100)))
					cost = cost + (line.purchase_price * line.product_uom_qty)
					hours = hours + line.product_uom_qty
		self.total_sp_work = sale
		self.total_cp_work = cost
		self.total_hours = hours
		if (hours != 0):
			self.sale_price_work_hour = sale/hours
			self.cost_price_work_hour = cost/hours
		if (cost != 0) and (sale != 0):
			self.benefit_work = (1-(cost/sale)) * 100

	#Recalcula los totales ideales al cambiar las horas
	@api.multi
	@api.onchange('total_hours')
	def _onchange_total_ideal(self):
		for record in self:
			record.total_ideal_hours = record.total_hours
			#record.sale_price_ideal_work_hour = record.sale_price_work_hour
			record.cost_price_ideal_work_hour = record.cost_price_work_hour

	#Calculo del precio de venta y coste ideal de los trabajos y su beneficio
	@api.multi
	@api.depends('sale_price_ideal_work_hour','cost_price_ideal_work_hour','total_ideal_hours')
	def _compute_price_work_ideal(self):
		for record in self:
			record.sale_price_ideal_work_hour = record.sale_price_work_hour
			#record.total_sp_ideal_work = record.total_ideal_hours * record.sale_price_ideal_work_hour
			record.total_sp_ideal_work = record.total_sp_work
			record.total_cp_ideal_work = record.total_ideal_hours * record.cost_price_ideal_work_hour
			if (record.total_cp_ideal_work != 0) and (record.total_sp_ideal_work != 0):
				record.benefit_ideal_work = (1-(record.total_cp_ideal_work/record.total_sp_ideal_work)) * 100


class SaleOrderLine(models.Model):

	_inherit='sale.order.line'

	#Campos relacionales para trabajos y materiales
	task_works_ids = fields.One2many(comodel_name='sale.order.line.task.work', inverse_name='order_line_id', string='Trabajos', copy=True)
	task_materials_ids = fields.One2many(comodel_name='sale.order.line.task.material', inverse_name='order_line_id', string='Materiales', copy=True)
	#Producto mano de obra
	workforce_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', copy=True)
	#Precio totales, unitarios y beneficio de Trabajos
	total_sp_work = fields.Float(string='Total P.V.', digits=dp.get_precision('Product Price'), compute='_compute_total_sp_work')
	total_cp_work = fields.Float(string='Total P.C.', digits=dp.get_precision('Product Price'), compute='_compute_total_cp_work')
	benefit_work = fields.Float(string='Beneficio', digits=dp.get_precision('Product Price'), compute='_compute_benefit_work')
	total_hours = fields.Float(string='Total horas', compute='_compute_total_hours')
	#Precios totales, unitarios  y beneficio de Materiales
	total_sp_material = fields.Float(string='Total P.V.', digits=dp.get_precision('Product Price'), compute='_compute_total_sp_material')
	total_cp_material = fields.Float(string='Total P.C.', digits=dp.get_precision('Product Price'), compute='_compute_total_cp_material')
	benefit_material = fields.Float(string='Beneficio', digits=dp.get_precision('Product Price'), compute='_compute_benefit_material')
	#Campo boolean para saber si crear o no una tarea de forma automatica
	auto_create_task = fields.Boolean(string='Tarea automática', copy=True)
	#Opciones de impresión por linea de pedido
	detailed_time = fields.Boolean(string='Imp. horas')
	detailed_price_time = fields.Boolean(string='Imp. precio Hr.')
	detailed_materials = fields.Boolean(string='Imp.materiales')
	detailed_price_materials = fields.Boolean(string='Imp. precio Mat.')

	#Calculo del precio total de venta de los trabajos
	@api.multi
	@api.depends('task_works_ids', 'task_works_ids.sale_price')
	def _compute_total_sp_work(self):
		for record in self:
			if record.task_works_ids:
				record.total_sp_work = sum(record.task_works_ids.mapped('sale_price'))

	#Calculo del precio total de coste de los trabajos
	@api.multi
	@api.depends('task_works_ids', 'task_works_ids.cost_price')
	def _compute_total_cp_work(self):
		for record in self:
			if record.task_works_ids:
				record.total_cp_work = sum(record.task_works_ids.mapped('cost_price'))

	#Calculo del total de horas de los trabajos
	@api.multi
	@api.depends('task_works_ids', 'task_works_ids.hours')
	def _compute_total_hours(self):
		for record in self:
			if record.task_works_ids:
				record.total_hours = sum(record.task_works_ids.mapped('hours'))

	#Calculo del beneficio de los trabajos
	@api.multi
	@api.depends('total_sp_work', 'total_cp_work')
	def _compute_benefit_work(self):
		for record in self:
			if (record.total_sp_work != 0) and (record.total_cp_work != 0):
				record.benefit_work = (1-(record.total_cp_work/record.total_sp_work)) * 100

	#Calculo del precio total de venta de los materiales
	@api.multi
	@api.depends('task_materials_ids', 'task_materials_ids.sale_price')
	def _compute_total_sp_material(self):
		for record in self:
			if record.task_materials_ids:
				record.total_sp_material = sum(record.task_materials_ids.mapped('sale_price'))

	#Calculo del precio total de coste de los materiales
	@api.multi
	@api.depends('task_materials_ids', 'task_materials_ids.cost_price')
	def _compute_total_cp_material(self):
		for record in self:
			if record.task_materials_ids:
				record.total_cp_material = sum(record.task_materials_ids.mapped('cost_price'))

	#Calculo del beneficio de los materiales
	@api.multi
	@api.depends('total_sp_material', 'total_cp_material')
	def _compute_benefit_material(self):
		for record in self:
			if (record.total_cp_material != 0) and (record.total_sp_material != 0):
				record.benefit_material = (1-(record.total_cp_material/record.total_sp_material)) * 100

	#Cambio de los precios unitarios de los trabajos al seleccionar la mano de obra
	#@api.onchange('workforce_id')
	#def _onchange_workforce_id(self):
	#	if self.task_works_ids:
	#		for record in self.task_works_ids:
	#			record.sale_price_unit = record.order_line_id.workforce_id.list_price
	#			record.cost_price_unit = record.order_line_id.workforce_id.standard_price

	def _get_real_price_line_currency(self, product, rule_id, qty, uom, pricelist_id):
		"""Retrieve the price before applying the pricelist
			:param obj product: object of current product record
			:parem float qty: total quentity of product
			:param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
			:param obj uom: unit of measure of current order line
			:param integer pricelist_id: pricelist id of sales order"""
		PricelistItem = self.env['product.pricelist.item']
		field_name = 'lst_price'
		currency_id = None
		product_currency = product.currency_id
		if rule_id:
			pricelist_item = PricelistItem.browse(rule_id)
			if pricelist_item.pricelist_id.discount_policy == 'without_discount':
				while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
					price, rule_id = pricelist_item.base_pricelist_id.with_context(uom=uom.id).get_product_price_rule(product, qty, self.order_id.partner_id)
					pricelist_item = PricelistItem.browse(rule_id)

			if pricelist_item.base == 'standard_price':
				field_name = 'standard_price'
				product_currency = product.cost_currency_id
			elif pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id:
				field_name = 'price'
				product = product.with_context(pricelist=pricelist_item.base_pricelist_id.id)
				product_currency = pricelist_item.base_pricelist_id.currency_id
			currency_id = pricelist_item.pricelist_id.currency_id

		if not currency_id:
			currency_id = product_currency
			cur_factor = 1.0
		else:
			if currency_id.id == product_currency.id:
				cur_factor = 1.0
			else:
				cur_factor = currency_id._get_conversion_rate(product_currency, currency_id)

		product_uom = self.env.context.get('uom') or product.uom_id.id
		if uom and uom.id != product_uom:
			# the unit price is in a different uom
			uom_factor = uom._compute_price(1.0, product.uom_id)
		else:
			uom_factor = 1.0

		if field_name == 'lst_price' or field_name == 'price':
			line_price = self.price_unit
		elif field_name == 'standard_price':
			line_price = self.purchase_price

		return line_price * uom_factor * cur_factor, currency_id.id

	#Obtiene el precio del material o mano de obra segun tarifa
	@api.multi
	def _get_display_price_line(self, product, product_id, quantity):
		if self.order_id.pricelist_id.discount_policy == 'with_discount':
			return product.with_context(pricelist=self.order_id.pricelist_id.id).price

		product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=product_id.uom_id.id)
		if self.auto_create_task:
			final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product_id, quantity or 1.0, self.order_id.partner_id)
			final_price = 0.0
			base_price, currency_id = self.with_context(product_context)._get_real_price_line_currency(product, rule_id, quantity, product_id.uom_id, self.order_id.pricelist_id.id)
		else:
			final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product_id, quantity or 1.0, self.order_id.partner_id)
			base_price, currency_id = self.with_context(product_context)._get_real_price_currency(product, rule_id, quantity, product_id.uom_id, self.order_id.pricelist_id.id)

		if currency_id != self.order_id.pricelist_id.currency_id.id:
			base_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(base_price, self.order_id.pricelist_id.currency_id)

		return max(base_price, final_price)

	#Calculo del descuento según la tarifa
	@api.multi
	def _get_discount_line(self, product_id, quantity):
		if not (product_id and product_id.uom_id and 
				self.order_id.partner_id and 
				self.order_id.pricelist_id and 
				self.order_id.pricelist_id.discount_policy == 'without_discount' and 
				self.env.user.has_group('sale.group_discount_per_so_line')):
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
		new_list_price, currency_id = self.with_context(product_context)._get_real_price_currency(product, rule_id, quantity, product_id.uom_id, self.order_id.pricelist_id.id)

		if new_list_price != 0:
			if self.order_id.pricelist_id.currency_id.id != currency_id:
				#necesitamos que new_list_price este en la misma moneda que price, 
				#la cual esta en la moneda de la tarida del presupuesto
				new_list_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(new_list_price, self.order_id.pricelist_id.currency_id)
			
			discount = (new_list_price - price) / new_list_price * 100
			if discount > 0:
				return discount

	#Carga de los datos del producto en la linea de pedido al seleccionar dicho producto
	@api.multi
	@api.onchange('product_id')
	def product_id_change(self):
		result = super(SaleOrderLine, self).product_id_change()
		product = self.product_id
		if product:
			self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_new_project')

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
					'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(mat, material.material_id, material.quantity), mat.taxes_id, self.tax_id, self.company_id),
					'cost_price_unit' : material.cost_price_unit,
					'quantity' : material.quantity,
					'discount' : self._get_discount_line(material.material_id, material.quantity) or 0.0
					}))

			self.update({'task_works_ids' : work_list,
					'task_materials_ids' : material_list,
					#'workforce_id' : product.workforce_id.id,
					'auto_create_task' : True})

			#for line in self:
			#	line.price_unit = (line.total_sp_material + line.total_sp_work)

		else:
			self.update({'task_works_ids' : False,
					'task_materials_ids' : False,
					#'workforce_id' : False,
					'auto_create_task' : False})
		return result

	#Calculo del precio de venta y coste del prodcuto tipo partida en la linea de pedido
	#al producirse algun cambio en los materiales, trabajos o mano de obra
	@api.multi
	@api.onchange('task_materials_ids', 'task_works_ids')
	def _onchange_task_materials_works_workforce(self):
		if not self.product_id:
			return
		for line in self:
			line.purchase_price = (line.total_cp_material + line.total_cp_work)
			product = line.product_id.with_context(
				lang=line.order_id.partner_id.lang,
				partner=line.order_id.partner_id.id,
				quantity=line.product_uom_qty,
				date=line.order_id.date_order,
				pricelist=line.order_id.pricelist_id.id,
				uom=line.product_uom.id
			)
			if line.purchase_price != line.product_id.standard_price:
				line.price_unit = self.env['account.tax']._fix_tax_included_price_company(line.purchase_price, product.taxes_id, self.tax_id, self.company_id)
			else:
				line.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
			#line.price_unit = (line.total_sp_material + line.total_sp_work)
			

	#Cuando se cambie la cantida o las unidades del producto aplique la tarifa a los trabajos y
	#materiales si es de tipo partida el producto
	@api.onchange('product_uom', 'product_uom_qty')
	def product_uom_change(self):
		result = super(SaleOrderLine, self).product_uom_change()
		product = self.product_id
		if product:
			self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_new_project')

		if self.auto_create_task:
			for line in self:
				product = line.product_id.with_context(
					lang=line.order_id.partner_id.lang,
					partner=line.order_id.partner_id.id,
					quantity=line.product_uom_qty,
					date=line.order_id.date_order,
					pricelist=line.order_id.pricelist_id.id,
					uom=line.product_uom.id
				)
				if line.purchase_price != line.product_id.standard_price:
					line.price_unit = self.env['account.tax']._fix_tax_included_price_company(line.purchase_price, product.taxes_id, self.tax_id, self.company_id)
				else:
					line.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)#line.price_unit = (line.total_sp_material + line.total_sp_work)
			
		return result

	#Calculo de las horas estimadas al crear el parte de trabajo correspondiente a la linea de pedido
	def _convert_qty_company_hours(self):
		company_time_uom_id = self.env.user.company_id.project_time_mode_id
		if self.product_uom.id != company_time_uom_id.id and self.product_uom.category_id.id == company_time_uom_id.category_id.id:
			planned_hours = self.product_uom._compute_quantity(self.product_uom_qty, company_time_uom_id)
		else:
			planned_hours = sum(self.task_works_ids.mapped('hours')) * self.product_uom_qty
			return planned_hours
	
	#Creación del proyecto
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
				if not project.sale_line_id and self.product_id.service_tracking in ['task_new_project', 'project_only']:
					project.write({'sale_line_id': self.id})
		return project

	#Calculo de los valores necesarios para crear el parte de trabajo correspondiente a la linea de pedido
	def _timesheet_create_task_prepare_values(self):
		self.ensure_one()
		project = self._timesheet_find_project()
		planned_hours = self._convert_qty_company_hours()

		work_list = []
		for work in self.task_works_ids:
			work_list.append((0,0, {
				'work_id' : work.work_id.id,
				'name' : work.name,
				'hours' : work.hours,
				}))

		material_list = []
		for material in self.task_materials_ids:
			material_list.append((0,0, {
				'product_id' : material.material_id.id,
				'quantity' : material.quantity * self.product_uom_qty,
				}))

		return {
			'name': '%s:%s' % (self.order_id.name or '', self.name.split(' ')[0] or self.product_id.name),
			'planned_hours': planned_hours,
			'remaining_hours': planned_hours,
			'partner_id': self.order_id.partner_id.id,
			'description': self.name + '<br/>',
			'work_to_do' : self.name + '<br/>',
			'project_id': project.id,
			'sale_line_id': self.id,
			'company_id': self.company_id.id,
			'email_from': self.order_id.partner_id.email,
			'user_id': False, # force non assigned task, as created as sudo()
			'material_ids': material_list,
			'task_works_ids': work_list,
			'oppor_id': self.order_id.opportunity_id.id or False, # Asocia con el aviso
			}

	#Calculo de los valores necesarios de la linea factura asociada a la linea de pedido, al crear la factura del pedido
	@api.multi
	def _prepare_invoice_line(self, qty):
		res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
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

			#res['workforce_id'] = self.workforce_id.id or False
			res['auto_create_task'] = self.auto_create_task
			res['detailed_time'] = self.detailed_time
			res['detailed_price_time'] = self.detailed_price_time
			res['detailed_materials'] = self.detailed_materials
			res['detailed_price_materials'] = self.detailed_price_materials

		return res

	#Valores para visualizar la tarea asociada a la linea de presupuesto
	@api.multi
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
		return result


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
	sale_price = fields.Float(string='Precio Venta', digits=dp.get_precision('Product Price'), compute="_compute_price")
	cost_price = fields.Float(string='Precio Coste', digits=dp.get_precision('Product Price'), compute="_compute_price")
	#Precios Unitarios para cada trabajo
	sale_price_unit = fields.Float(string='P.V. unitario', digits=dp.get_precision('Product Price'))
	cost_price_unit = fields.Float(string='P.C. unitario', digits=dp.get_precision('Product Price'))
	#Horas empleadas en el trabajo
	hours = fields.Float(string='Horas')
	#Descuento aplicado al precio de la mano de obra
	discount = fields.Float(string='Descuento (%)', digits=dp.get_precision('Discount'), default=0.0)
	sequence = fields.Integer()

	#Obtiene el precio de la mano de obra segun tarifa
	@api.multi
	def _get_display_price_workforce(self, workforce):
		if self.order_line_id.order_id.pricelist_id.discount_policy == 'with_discount':
			return workforce.with_context(pricelist=self.order_line_id.order_id.pricelist_id.id).price

		workforce_context = dict(self.env.context, partner_id=self.order_line_id.order_id.partner_id.id, date=self.order_line_id.order_id.date_order, uom=self.work_id.uom_id.id)
		final_price, rule_id = self.order_line_id.order_id.pricelist_id.with_context(workforce_context).get_product_price_rule(self.work_id, self.hours or 1.0, self.order_line_id.order_id.partner_id)
		base_price, currency_id = self.order_line_id.with_context(workforce_context)._get_real_price_currency(workforce, rule_id, self.hours, self.work_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		if currency_id != self.order_line_id.order_id.pricelist_id.currency_id.id:
			base_price = self.env['res.currency'].browse(currency_id).with_context(workforce_context).compute(base_price, self.order_line_id.order_id.pricelist_id.currency_id)

		return max(base_price, final_price)

	#Calculo del precio de venta y coste unitario segun tarifa al cambiar las horas
	@api.multi
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
	
	#Carga de los valores en la linea de la mano de obra seleccionada
	@api.multi
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
				self.env.user.has_group('sale.group_discount_per_so_line')):
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
		new_list_price, currency_id = self.order_line_id.with_context(workforce_context)._get_real_price_currency(workforce, rule_id, self.hours, self.work_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		if new_list_price != 0:
			if self.order_line_id.order_id.pricelist_id.currency_id.id != currency_id:
				#necesitamos que new_list_price este en la misma moneda que price, 
				#la cual esta en la moneda de la tarida del presupuesto
				new_list_price = self.env['res.currency'].browse(currency_id).with_context(workforce_context).compute(new_list_price, self.order_line_id.order_id.pricelist_id.currency_id)
			
			discount = (new_list_price - price) / new_list_price * 100
			if discount > 0:
				self.discount = discount

	#Calculo de los precios de venta y coste totales por linea de los trabajos
	#@api.one
	@api.depends('hours','sale_price_unit', 'cost_price_unit', 'discount')
	def _compute_price(self):
		for record in self:
			record.sale_price = record.hours * (record.sale_price_unit * (1 - (record.discount / 100)))
			record.cost_price = (record.hours * record.cost_price_unit)

class SaleOrderLineTaskMaterial(models.Model):
	"""Modelo para almacenar los materiales del producto partida en la linea de pedido"""
	
	_name = 'sale.order.line.task.material'
	_order = 'order_line_id, sequence, id'

	#Campo relación con la linea de pedido
	order_line_id = fields.Many2one(comodel_name='sale.order.line', string='Linea de pedido')
	#Material
	material_id = fields.Many2one(comodel_name='product.product', string='Material', required=True)
	#Precios Totales de para cada material
	sale_price = fields.Float(string='Precio Venta', digits=dp.get_precision('Product Price'), compute='_compute_price')
	cost_price = fields.Float(string='Precio Coste', digits=dp.get_precision('Product Price'), compute='_compute_price')
	#Precios Unitarios para cada material
	sale_price_unit = fields.Float(string='P.V. unitario', digits=dp.get_precision('Product Price'))
	cost_price_unit = fields.Float(string='P.C. unitario', digits=dp.get_precision('Product Price'))
	#Cantidad de cada material
	quantity = fields.Float(string='Cantidad', digits=dp.get_precision('Product Unit of Measure'))
	#Descuento aplicado al precio del material
	discount = fields.Float(string='Descuento (%)', digits=dp.get_precision('Discount'), default=0.0)
	sequence = fields.Integer()

	#Obtiene el precio del material segun tarifa
	@api.multi
	def _get_display_price_material(self, material):
		if self.order_line_id.order_id.pricelist_id.discount_policy == 'with_discount':
			return material.with_context(pricelist=self.order_line_id.order_id.pricelist_id.id).price

		material_context = dict(self.env.context, partner_id=self.order_line_id.order_id.partner_id.id, date=self.order_line_id.order_id.date_order, uom=self.material_id.uom_id.id)
		final_price, rule_id = self.order_line_id.order_id.pricelist_id.with_context(material_context).get_product_price_rule(self.material_id, self.quantity or 1.0, self.order_line_id.order_id.partner_id)
		base_price, currency_id = self.order_line_id.with_context(material_context)._get_real_price_currency(material, rule_id, self.quantity, self.material_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		if currency_id != self.order_line_id.order_id.pricelist_id.currency_id.id:
			base_price = self.env['res.currency'].browse(currency_id).with_context(material_context).compute(base_price, self.order_line_id.order_id.pricelist_id.currency_id)

		return max(base_price, final_price)

	#Carga de los valores en la linea del material seleccionado
	@api.multi
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

	#Calculo del precio de venta y coste unitario segun tarifa al cambiar la cantidad
	@api.multi
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
				self.env.user.has_group('sale.group_discount_per_so_line')):
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
		new_list_price, currency_id = self.order_line_id.with_context(mat_context)._get_real_price_currency(mat, rule_id, self.quantity, self.material_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		if new_list_price != 0:
			if self.order_line_id.order_id.pricelist_id.currency_id.id != currency_id:
				#necesitamos que new_list_price este en la misma moneda que price, 
				#la cual esta en la moneda de la tarida del presupuesto
				new_list_price = self.env['res.currency'].browse(currency_id).with_context(mat_context).compute(new_list_price, self.order_line_id.order_id.pricelist_id.currency_id)
			
			discount = (new_list_price - price) / new_list_price * 100
			if discount > 0:
				self.discount = discount

	#Calculo de los precios de venta y coste totales por linea de los materiales
	#@api.one
	@api.depends('quantity','sale_price_unit','cost_price_unit','discount')
	def _compute_price(self):
		for record in self:
				record.sale_price = record.quantity * (record.sale_price_unit * (1 - (record.discount / 100)))
				record.cost_price = (record.quantity * record.cost_price_unit)
