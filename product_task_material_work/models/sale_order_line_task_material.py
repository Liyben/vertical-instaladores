# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLineTaskMaterial(models.Model):
	"""Modelo para almacenar los materiales del producto partida en la linea de pedido"""
	
	_name = 'sale.order.line.task.material'
	_description = "Sale Order Line Task Material"
	_order = 'order_line_id, sequence, id'
	_check_company_auto = True

	#Dominio para el campo material
	@api.model
	def _get_material_id_domain(self):
		uom_categ_id = self.env.ref('uom.uom_categ_wtime').id
		return [('uom_id.category_id', '!=', uom_categ_id), ('sale_ok', '=', True)]

	#Descripcion del material
	name = fields.Char(string='Descripción', required=True)
	#Campo relación con la linea de pedido
	order_line_id = fields.Many2one(comodel_name='sale.order.line', string='Linea de pedido')
	#Material
	material_id = fields.Many2one(comodel_name='product.product', string='Material', required=True, domain=_get_material_id_domain, check_company=True)
	#Precios Totales de para cada material
	sale_price = fields.Float(string='P.V.', digits='Product Price', compute='_compute_price')
	cost_price = fields.Float(string='P.C.', digits='Product Price', compute='_compute_price')
	#Precios Unitarios para cada material
	sale_price_unit = fields.Float(string='P.V.U.', digits='Product Price')
	cost_price_unit = fields.Float(string='P.C.U.', digits='Product Price')
	#Cantidad de cada material
	quantity = fields.Float(string='Und.', digits='Product Unit of Measure', default=1.0)
	#Descuento aplicado al precio del material
	discount = fields.Float(string='Des. (%)', digits='Discount', default=0.0)
	sequence = fields.Integer()
	#Margen
	material_margin = fields.Float(string='Margen', digits='Product Price', compute='_compute_price')
	material_margin_percent = fields.Float(string='Margen (%)', digits='Product Price', compute='_compute_price')
	#Misma compañia que el pedido al que pertence
	company_id = fields.Many2one(related='order_line_id.order_id.company_id', store=True, index=True, precompute=True)
	#Misma moneda que el pedido al que pertenece
	currency_id = fields.Many2one(related='order_line_id.order_id.currency_id', depends=['product_id.currency_id'], store=True, precompute=True) 

	""" #Obtiene el precio del material segun tarifa
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

				material = record.material_id.with_context(
					lang=record.order_line_id.order_id.partner_id.lang,
					partner=record.order_line_id.order_id.partner_id.id,
					quantity=record.quantity,
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
	@api.depends('quantity','sale_price_unit','cost_price_unit','discount')
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
				record.material_margin_percent = (1-(record.cost_price/record.sale_price)) """
