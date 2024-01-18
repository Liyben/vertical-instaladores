# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class SaleOrder(models.Model):
	"""docstring for SaleOrder"""
	_inherit='sale.order'

	#Opciones de impresión
	detailed_time = fields.Boolean(string='Imp. horas')
	detailed_price_time = fields.Boolean(string='Imp. precio Hr.')
	detailed_materials = fields.Boolean(string='Imp.materiales')
	detailed_price_materials = fields.Boolean(string='Imp. precio Mat.')
	detailed_subtotal_price_time = fields.Boolean(string='Imp. subtotal Hr.')
	detailed_subtotal_price_materials = fields.Boolean(string='Imp. subtotal Mat.')

	#Modificamos la impresion del subtotal de las horas de todas las lineas
	@api.onchange('detailed_subtotal_price_time')
	def print_detailed_subtotal_price_time(self):
		for sale in self:
			#sale.detailed_subtotal_price_time = not sale.detailed_subtotal_price_time

			for line in sale.order_line:
				if line.auto_create_task:
					line.detailed_subtotal_price_time = sale.detailed_subtotal_price_time

	#Modificamos la impresion del subtotal de los materiales de todas las lineas
	@api.onchange('detailed_subtotal_price_materials')
	def print_detailed_subtotal_price_materials(self):
		for sale in self:
			#sale.detailed_subtotal_price_materials = not sale.detailed_subtotal_price_materials

			for line in sale.order_line:
				if line.auto_create_task:
					line.detailed_subtotal_price_materials = sale.detailed_subtotal_price_materials

	#Modificamos la impresion de horas de todas las lineas
	@api.onchange('detailed_time')
	def print_detailed_time(self):
		for sale in self:
			#sale.detailed_time = not sale.detailed_time

			for line in sale.order_line:
				if line.auto_create_task:
					line.detailed_time = sale.detailed_time

	#Modificamos la impresion de horas con precio de todas las lineas
	@api.onchange('detailed_price_time')
	def print_detailed_price_time(self):
		for sale in self:
			#sale.detailed_price_time = not sale.detailed_price_time

			for line in sale.order_line:
				if line.auto_create_task:
					line.detailed_price_time = sale.detailed_price_time

	#Modificamos la impresion de materiales de todas las lineas
	@api.onchange('detailed_materials')
	def print_detailed_materials(self):
		for sale in self:
			#sale.detailed_materials = not sale.detailed_materials

			for line in sale.order_line:
				if line.auto_create_task:
					line.detailed_materials = sale.detailed_materials

	#Modificamos la impresion de materiales con precio de todas las lineas
	@api.onchange('detailed_price_materials')
	def print_detailed_price_materials(self):
		for sale in self:
			#sale.detailed_price_materials = not sale.detailed_price_materials

			for line in sale.order_line:
				if line.auto_create_task:
					line.detailed_price_materials = sale.detailed_price_materials

