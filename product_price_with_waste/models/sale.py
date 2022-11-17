# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

class SaleOrderLine(models.Model):

	_inherit='sale.order.line'


	# % desperdicio
	percent_waste = fields.Float(string='% Desperdicio', digits='Discount')

	#Carga de los datos del producto en la linea de pedido al seleccionar dicho producto
	
	@api.onchange('product_id')
	def product_id_change(self):
		result = super(SaleOrderLine, self).product_id_change()
		product = self.product_id
		if product:
			self.percent_waste = product.percent_waste
		
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
					'standard_price' : (line.total_cp_material + line.total_cp_work) + ((line.total_cp_material + line.total_cp_work) * (line.percent_waste / 100)),
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

				line.purchase_price = (line.total_cp_material + line.total_cp_work) + ((line.total_cp_material + line.total_cp_work) * (line.percent_waste / 100))

				#Recuperamos los precios de la ficha producto previamente guardado
				line.product_id.write({
					'lst_price' : product_lst_price,
					'standard_price' : product_standard_price,
				})


	#Cuando se cambie la cantida o las unidades del producto aplique la tarifa a los trabajos y
	#materiales si es de tipo partida el producto
	@api.onchange('product_uom', 'product_uom_qty')
	def product_uom_change(self):
		#result = super(SaleOrderLine, self).product_uom_change()
		product = self.product_id
		if product:
			self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_in_project')

		if self.auto_create_task and self.order_id.pricelist_id and self.order_id.partner_id and self.percent_waste > 0.0:
			for line in self:
				#Guardamos los precios de la ficha de producto
				product_lst_price = line.product_id.lst_price
				product_standard_price = line.product_id.standard_price

				#Actualizamos los precios de la ficha de producto con los precios de la linea de pedido
				line.product_id.write({
					'lst_price' : (line.total_sp_material + line.total_sp_work),
					'standard_price' : (line.total_cp_material + line.total_cp_work) + ((line.total_cp_material + line.total_cp_work) * (line.percent_waste / 100)),
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
				
				line.purchase_price = (line.total_cp_material + line.total_cp_work) + ((line.total_cp_material + line.total_cp_work) * (line.percent_waste / 100))

				#Recuperamos los precios de la ficha producto previamente guardado
				line.product_id.write({
					'lst_price' : product_lst_price,
					'standard_price' : product_standard_price,
				})
		else:
			super(SaleOrderLine, self).product_uom_change()
		#return result

	#Función que recalcula el precio de venta y coste del compuesto
	def product_action_recalculate(self):
		if self.auto_create_task and self.order_id.pricelist_id and self.order_id.partner_id:
			for line in self:
				#Guardamos los precios de la ficha de producto
				product_lst_price = line.product_id.lst_price
				product_standard_price = line.product_id.standard_price

				#Actualizamos los precios de la ficha de producto con los precios de la linea de pedido
				line.product_id.write({
					'lst_price' : (line.total_sp_material + line.total_sp_work),
					'standard_price' : (line.total_cp_material + line.total_cp_work) + ((line.total_cp_material + line.total_cp_work) * (line.percent_waste / 100)),
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

				line.purchase_price = (line.total_cp_material + line.total_cp_work) + ((line.total_cp_material + line.total_cp_work) * (line.percent_waste / 100))

				#Recuperamos los precios de la ficha producto previamente guardado
				line.product_id.write({
					'lst_price' : product_lst_price,
					'standard_price' : product_standard_price,
				})

	#Calculo del precio de venta y coste del prodcuto tipo partida en la linea de pedido
	#al producirse algun cambio en el % de desperdicio
	@api.onchange('percent_waste')
	def _onchange_percent_waste(self):
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
					'standard_price' : (line.total_cp_material + line.total_cp_work) + ((line.total_cp_material + line.total_cp_work) * (line.percent_waste / 100)),
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

				line.purchase_price = (line.total_cp_material + line.total_cp_work) + ((line.total_cp_material + line.total_cp_work) * (line.percent_waste / 100))

				#Recuperamos los precios de la ficha producto previamente guardado
				line.product_id.write({
					'lst_price' : product_lst_price,
					'standard_price' : product_standard_price,
				})