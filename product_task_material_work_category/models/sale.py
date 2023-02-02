# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):

	_inherit='sale.order.line'

	#Carga de los datos del producto en la linea de pedido al seleccionar dicho producto
	
	@api.onchange('product_id')
	def product_id_change(self):
		result = super(SaleOrderLine, self).product_id_change()
		product = self.product_id
		if product:
			self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_in_project')

		if self.auto_create_task:
			self.update({'task_works_ids' : False,
					'task_materials_ids' : False,})

			work_list = []
			for work in product.task_works_ids:
				#Se guarda la categoria de la mano de obra y se le asigna la categoria del compuesto
				category_work = False
				hours = work.hours
				if self.product_id.apply_category:
					category_work = work.work_id.categ_id.id
					hours = self.product_uom_qty
					work.work_id.write({
						'categ_id' : self.product_id.categ_id.id
					})

				workforce = work.work_id.with_context(
					lang=self.order_id.partner_id.lang,
					partner=self.order_id.partner_id.id,
					quantity=hours,
					date=self.order_id.date_order,
					pricelist=self.order_id.pricelist_id.id,
					uom=work.work_id.uom_id.id)

				work_list.append((0,0, {
					'name' : work.name,
					'work_id': work.work_id.id,
					'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(workforce, work.work_id, hours), workforce.taxes_id, self.tax_id, self.company_id),
					'cost_price_unit' : work.cost_price_unit,
					'hours' : work.hours,
					'discount' : self._get_discount_line(work.work_id, work.hours) or 0.0
					}))

				#Se recupera la categoria
				if self.product_id.apply_category:
					work.work_id.write({
						'categ_id' : category_work
					})

			material_list = []
			for material in product.task_materials_ids:
				#Se guarda la categoria del material y se le asigna la categoria del compuesto
				category_material = False
				quantity = material.quantity
				if self.product_id.apply_category:
					category_material = material.material_id.categ_id.id
					quantity = self.product_uom_qty
					material.material_id.write({
						'categ_id' : self.product_id.categ_id.id
					})

				mat = material.material_id.with_context(
						lang=self.order_id.partner_id.lang,
						partner=self.order_id.partner_id.id,
						quantity=quantity,
						date=self.order_id.date_order,
						pricelist=self.order_id.pricelist_id.id,
						uom=material.material_id.uom_id.id)

				material_list.append((0,0, {
					'material_id' : material.material_id.id,
					'name' : material.name,
					'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(mat, material.material_id, quantity), mat.taxes_id, self.tax_id, self.company_id),
					'cost_price_unit' : material.cost_price_unit,
					'quantity' : material.quantity,
					'discount' : self._get_discount_line(material.material_id, material.quantity) or 0.0
					}))

				#Se recupera la categoria
				if self.product_id.apply_category:
					material.material_id.write({
						'categ_id' : category_material
					})

			self.update({'task_works_ids' : work_list,
					'task_materials_ids' : material_list,
					'auto_create_task' : True,})

			#for line in self:
			#	line.price_unit = (line.total_sp_material + line.total_sp_work)

		else:
			self.update({'task_works_ids' : False,
					'task_materials_ids' : False,
					'auto_create_task' : False,})

		return result

	#Calculo del descuento según la tarifa
	
	def _get_discount_line(self, product_id, quantity):
		if not (product_id and product_id.uom_id and 
				self.order_id.partner_id and 
				self.order_id.pricelist_id and 
				self.order_id.pricelist_id.discount_policy == 'without_discount' and 
				self.env.user.has_group('product.group_discount_per_so_line')):
			return

		#Se guarda la categoria y se le asigna la categoria del compuesto
		category = False
		if self.product_id.apply_category:
			category = product_id.categ_id.id
			quantity = self.product_uom_qty
			product_id.write({
				'categ_id' : self.product_id.categ_id.id
			})

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

		#Se recupera la categoria
		if self.product_id.apply_category:
			product_id.write({
				'categ_id' : category
			})

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


class SaleOrderLineTaskWork(models.Model):
	"""Modelo para almacenar los trabajos del producto partida en la linea de pedido"""

	_inherit = 'sale.order.line.task.work'

	#Obtiene el precio de la mano de obra segun tarifa
	
	def _get_display_price_workforce(self, workforce):
		if self.order_line_id.order_id.pricelist_id.discount_policy == 'with_discount':
			return workforce.with_context(pricelist=self.order_line_id.order_id.pricelist_id.id).price

		hours = self.hours
		if self.order_line_id.product_id.apply_category:
			hours = self.order_line_id.product_uom_qty

		workforce_context = dict(self.env.context, partner_id=self.order_line_id.order_id.partner_id.id, date=self.order_line_id.order_id.date_order, uom=self.work_id.uom_id.id)
		final_price, rule_id = self.order_line_id.order_id.pricelist_id.with_context(workforce_context).get_product_price_rule(self.work_id, hours or 1.0, self.order_line_id.order_id.partner_id)
		base_price, currency = self.order_line_id.with_context(workforce_context)._get_real_price_currency(workforce, rule_id, hours, self.work_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		if currency != self.order_line_id.order_id.pricelist_id.currency_id:
			base_price = currency._convert(
				base_price, self.order_line_id.order_id.pricelist_id.currency_id,
				self.order_line_id.order_id.company_id or self.env.company, self.order_line_id.order_id.date_order or fields.Date.today())

		return max(base_price, final_price)

	#Calculo del precio de venta y coste unitario segun tarifa al cambiar las horas
	
	@api.onchange('hours','cost_price_unit')
	def _onchange_hours(self):
		for record in self:
			if record.work_id:
				#Guardamos los precios de la ficha de producto
				product_lst_price = record.work_id.lst_price
				product_standard_price = record.work_id.standard_price

				#Actualizamos los precios de la ficha de producto con los precios de la linea de pedido
				record.work_id.write({
					'lst_price' : record.sale_price_unit,
					'standard_price' : record.cost_price_unit,
				})

				#Se guarda la categoria de la mano de obra y se le asigna la categoria del compuesto
				category = False
				hours = record.hours
				if record.order_line_id.product_id.apply_category:
					category = record.work_id.categ_id.id
					hours = record.order_line_id.product_uom_qty
					record.work_id.write({
						'categ_id' : record.order_line_id.product_id.categ_id.id
					})

				workforce = record.work_id.with_context(
					lang=record.order_line_id.order_id.partner_id.lang,
					partner=record.order_line_id.order_id.partner_id.id,
					quantity=hours,
					date=record.order_line_id.order_id.date_order,
					pricelist=record.order_line_id.order_id.pricelist_id.id,
					uom=record.work_id.uom_id.id)

				record.sale_price_unit = record.order_line_id.env['account.tax']._fix_tax_included_price_company(self._get_display_price_workforce(workforce), workforce.taxes_id, self.order_line_id.tax_id, self.order_line_id.company_id)
				#record.cost_price_unit = record.work_id.standard_price
				#record.name = record.work_id.name

				#Recuperamos los precios de la ficha producto previamente guardado
				record.work_id.write({
					'lst_price' : product_lst_price,
					'standard_price' : product_standard_price,
				})

				#Se recupera la categoria de la mano de obra
				if record.order_line_id.product_id.apply_category:
					record.work_id.write({
						'categ_id' : category
					})
	
	#Carga de los valores en la linea de la mano de obra seleccionada
	
	@api.onchange('work_id')
	def _onchange_work_id(self):
		for record in self:
			if record.work_id:
				#Se guarda la categoria de la mano de obra y se le asigna la categoria del compuesto
				category = False
				hours = record.hours
				if record.order_line_id.product_id.apply_category:
					category = record.work_id.categ_id.id
					hours = record.order_line_id.product_uom_qty
					record.work_id.write({
						'categ_id' : record.order_line_id.product_id.categ_id.id
					})

				workforce = record.work_id.with_context(
					lang=record.order_line_id.order_id.partner_id.lang,
					partner=record.order_line_id.order_id.partner_id.id,
					quantity=hours,
					date=record.order_line_id.order_id.date_order,
					pricelist=record.order_line_id.order_id.pricelist_id.id,
					uom=record.work_id.uom_id.id)

				record.sale_price_unit = record.order_line_id.env['account.tax']._fix_tax_included_price_company(self._get_display_price_workforce(workforce), workforce.taxes_id, self.order_line_id.tax_id, self.order_line_id.company_id)
				record.cost_price_unit = record.work_id.standard_price
				#Se recupera la categoria de la mano de obra
				if record.order_line_id.product_id.apply_category:
					record.work_id.write({
						'categ_id' : category
					})
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
		#Se guarda la categoria de la mano de obra y se le asigna la categoria del compuesto
		category = False
		hours = self.hours
		if self.order_line_id.product_id.apply_category:
			category = self.work_id.categ_id.id
			hours = self.order_line_id.product_uom_qty
			self.work_id.write({
				'categ_id' : self.order_line_id.product_id.categ_id.id
			})

		workforce = self.work_id.with_context(
			lang=self.order_line_id.order_id.partner_id.lang,
			partner=self.order_line_id.order_id.partner_id.id,
			quantity=hours,
			date=self.order_line_id.order_id.date_order,
			pricelist=self.order_line_id.order_id.pricelist_id.id,
			uom=self.work_id.uom_id.id,
			fiscal_position=self.env.context.get('fiscal_position'))

		workforce_context = dict(self.env.context, partner_id=self.order_line_id.order_id.partner_id.id, date=self.order_line_id.order_id.date_order, uom=self.work_id.uom_id.id)

		price, rule_id = self.order_line_id.order_id.pricelist_id.with_context(workforce_context).get_product_price_rule(self.work_id, hours or 1.0, self.order_line_id.order_id.partner_id)
		new_list_price, currency = self.order_line_id.with_context(workforce_context)._get_real_price_currency(workforce, rule_id, hours, self.work_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		#Se recupera la categoria del material
		if self.order_line_id.product_id.apply_category:
			self.work_id.write({
				'categ_id' : category
			})

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

class SaleOrderLineTaskMaterial(models.Model):
	"""Modelo para almacenar los materiales del producto partida en la linea de pedido"""
	
	_inherit = 'sale.order.line.task.material'

	#Obtiene el precio del material segun tarifa
	
	def _get_display_price_material(self, material):
		if self.order_line_id.order_id.pricelist_id.discount_policy == 'with_discount':
			return material.with_context(pricelist=self.order_line_id.order_id.pricelist_id.id).price

		quantity = self.quantity
		if self.order_line_id.product_id.apply_category:
			quantity = self.order_line_id.product_uom_qty

		material_context = dict(self.env.context, partner_id=self.order_line_id.order_id.partner_id.id, date=self.order_line_id.order_id.date_order, uom=self.material_id.uom_id.id)
		final_price, rule_id = self.order_line_id.order_id.pricelist_id.with_context(material_context).get_product_price_rule(self.material_id, quantity or 1.0, self.order_line_id.order_id.partner_id)
		base_price, currency = self.order_line_id.with_context(material_context)._get_real_price_currency(material, rule_id, quantity, self.material_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

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
				#Se guarda la categoria del material y se le asigna la categoria del compuesto
				category = False
				quantity = record.quantity
				if record.order_line_id.product_id.apply_category:
					category = record.material_id.categ_id.id
					quantity = record.order_line_id.product_uom_qty
					record.material_id.write({
						'categ_id' : record.order_line_id.product_id.categ_id.id
					})

				material = record.material_id.with_context(
					lang=record.order_line_id.order_id.partner_id.lang,
					partner=record.order_line_id.order_id.partner_id.id,
					quantity=quantity,
					date=record.order_line_id.order_id.date_order,
					pricelist=record.order_line_id.order_id.pricelist_id.id,
					uom=record.material_id.uom_id.id)
			
				record.sale_price_unit = record.order_line_id.env['account.tax']._fix_tax_included_price_company(self._get_display_price_material(material), material.taxes_id, self.order_line_id.tax_id, self.order_line_id.company_id)
				record.cost_price_unit = record.material_id.standard_price

				#Se recupera la categoria del material
				if record.order_line_id.product_id.apply_category:
					record.material_id.write({
						'categ_id' : category
					})
				#record.quantity = 1.0
				record.name = record.material_id.name

	#Calculo del precio de venta y coste unitario segun tarifa al cambiar la cantidad
	
	@api.onchange('quantity','cost_price_unit')
	def _onchange_quantity(self):
		for record in self:
			if record.material_id:
				#Guardamos los precios de la ficha de producto
				product_lst_price = record.material_id.lst_price
				product_standard_price = record.material_id.standard_price

				#Actualizamos los precios de la ficha de producto con los precios de la linea de pedido
				record.material_id.write({
					'lst_price' : record.sale_price_unit,
					'standard_price' : record.cost_price_unit,
				})

				#Se guarda la categoria del material y se le asigna la categoria del compuesto
				category = False
				quantity = record.quantity
				if record.order_line_id.product_id.apply_category:
					category = record.material_id.categ_id.id
					quantity = record.order_line_id.product_uom_qty
					record.material_id.write({
						'categ_id' : record.order_line_id.product_id.categ_id.id
					})

				material = record.material_id.with_context(
					lang=record.order_line_id.order_id.partner_id.lang,
					partner=record.order_line_id.order_id.partner_id.id,
					quantity=quantity,
					date=record.order_line_id.order_id.date_order,
					pricelist=record.order_line_id.order_id.pricelist_id.id,
					uom=record.material_id.uom_id.id)
			
				record.sale_price_unit = record.order_line_id.env['account.tax']._fix_tax_included_price_company(self._get_display_price_material(material), material.taxes_id, self.order_line_id.tax_id, self.order_line_id.company_id)
				#record.cost_price_unit = record.material_id.standard_price

				#Recuperamos los precios de la ficha producto previamente guardado
				record.material_id.write({
					'lst_price' : product_lst_price,
					'standard_price' : product_standard_price,
				})

				#Se recupera la categoria del material
				if record.order_line_id.product_id.apply_category:
					record.material_id.write({
						'categ_id' : category
					})

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
		#Se guarda la categoria del material y se le asigna la categoria del compuesto
		category = False
		quantity = self.quantity
		if self.order_line_id.product_id.apply_category:
			category = self.material_id.categ_id.id
			quantity = self.order_line_id.product_uom_qty
			self.material_id.write({
				'categ_id' : self.order_line_id.product_id.categ_id.id
			})
			

		mat = self.material_id.with_context(
			lang=self.order_line_id.order_id.partner_id.lang,
			partner=self.order_line_id.order_id.partner_id.id,
			quantity=quantity,
			date=self.order_line_id.order_id.date_order,
			pricelist=self.order_line_id.order_id.pricelist_id.id,
			uom=self.material_id.uom_id.id,
			fiscal_position=self.env.context.get('fiscal_position'))

		mat_context = dict(self.env.context, partner_id=self.order_line_id.order_id.partner_id.id, date=self.order_line_id.order_id.date_order, uom=self.material_id.uom_id.id)

		price, rule_id = self.order_line_id.order_id.pricelist_id.with_context(mat_context).get_product_price_rule(self.material_id, quantity or 1.0, self.order_line_id.order_id.partner_id)
		new_list_price, currency = self.order_line_id.with_context(mat_context)._get_real_price_currency(mat, rule_id, quantity, self.material_id.uom_id, self.order_line_id.order_id.pricelist_id.id)

		#Se recupera la categoria del material
		if self.order_line_id.product_id.apply_category:
			self.material_id.write({
				'categ_id' : category
			})

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
