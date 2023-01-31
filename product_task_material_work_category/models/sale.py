# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):

	_inherit='sale.order.line'

	#Obtiene el precio del material o mano de obra segun tarifa
	
	def _get_display_price_line(self, product, product_id, quantity):

		#Se guarda la categoria de la mano de obra y se le asigna la categoria del compuesto
		category = False
		if self.product_id.apply_category:
			category = product_id.categ_id.id
			product_id.write({
				'categ_id' : self.product_id.categ_id.id
			})
			product = product_id.with_context(
				lang=self.order_id.partner_id.lang,
				partner=self.order_id.partner_id.id,
				quantity=quantity,
				date=self.order_id.date_order,
				pricelist=self.order_id.pricelist_id.id,
				uom=product_id.uom_id.id)
		
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
			#Se recupera la categoria del material
			if self.product_id.apply_category:
				product_id.write({
					'categ_id' : category
				})

			return product.with_context(pricelist=self.order_id.pricelist_id.id).price

		product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=product_id.uom_id.id)
		final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product_id, quantity or 1.0, self.order_id.partner_id)
		base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, quantity, product_id.uom_id, self.order_id.pricelist_id.id)

		if currency != self.order_id.pricelist_id.currency_id:
			base_price = currency._convert(
				base_price, self.order_id.pricelist_id.currency_id,
				self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())

		#Se recupera la categoria del material
		if self.product_id.apply_category:
			product_id.write({
				'categ_id' : category
			})

		return max(base_price, final_price)

	#Calculo del descuento según la tarifa
	
	def _get_discount_line(self, product_id, quantity):
		if not (product_id and product_id.uom_id and 
				self.order_id.partner_id and 
				self.order_id.pricelist_id and 
				self.order_id.pricelist_id.discount_policy == 'without_discount' and 
				self.env.user.has_group('product.group_discount_per_so_line')):
			return

		#Se guarda la categoria de la mano de obra y se le asigna la categoria del compuesto
		category = False
		if self.product_id.apply_category:
			category = product_id.categ_id.id
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

		#Se recupera la categoria del material
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

	_name = 'sale.order.line.task.work'

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
				""" category = False
				if record.order_line_id.product_id.apply_category:
					category = record.work_id.categ_id.id
					record.work_id.write({
						'categ_id' : record.order_line_id.product_id.categ_id.id
					}) """

				workforce = record.work_id.with_context(
					lang=record.order_line_id.order_id.partner_id.lang,
					partner=record.order_line_id.order_id.partner_id.id,
					quantity=record.hours,
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
				""" if record.order_line_id.product_id.apply_category:
					record.work_id.write({
						'categ_id' : category
					}) """
	
	