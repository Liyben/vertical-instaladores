# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	secciones_ids = fields.One2many(
		comodel_name = 'sale.order.line.secciones',
		inverse_name = 'order_line_id',
		copy = True,
		string = 'Secciones')

	total_lineales = fields.Float(
		string = "T-mts. lineales",
		compute = '_compute_total_secciones',
		readonly = True,
		digits="Product Unit Of Measure")

	total_cuadrados = fields.Float(
		string = "T-mts. cuadrados",
		compute = '_compute_total_secciones',
		readonly = True,
		digits="Product Unit Of Measure")

	manual_mode = fields.Boolean(string='Modo manual')

	total_lineales_manual = fields.Float(
		string = "T-mts. lineales",
		digits="Product Unit Of Measure")

	total_cuadrados_manual = fields.Float(
		string = "T-mts. cuadrados",
		digits="Product Unit Of Measure")
	
	@api.onchange('total_lineales','total_cuadrados','manual_mode')
	def _onchange_metros(self):
		# Obtenemos el id de la unidad de medida ml y m2
		ml_id = self.env.ref('sale_order_line_sections.product_uom_lineal_meter').id
		m2_id = self.env.ref('sale_order_line_sections.product_uom_square_meter').id

		for material in self.task_materials_ids:
			# Comparamos el id de la unidad de medida del producto con ml_id
			if (material.material_id.uom_id.id == ml_id):
				material.quantity = self.total_lineales
			# Comparamos el id de la unidad de medida del producto con m2_id
			elif (material.material_id.uom_id.id == m2_id):
				material.quantity = self.total_cuadrados

	
	@api.onchange('total_lineales_manual','total_cuadrados_manual')
	def _onchange_metros_manual(self):
		# Obtenemos el id de la unidad de medida ml y m2
		ml_id = self.env.ref('sale_order_line_sections.product_uom_lineal_meter').id
		m2_id = self.env.ref('sale_order_line_sections.product_uom_square_meter').id

		for material in self.task_materials_ids:
			# Comparamos el id de la unidad de medida del producto con ml_id
			if (material.material_id.uom_id.id == ml_id):
				material.quantity = self.total_lineales_manual
			# Comparamos el id de la unidad de medida del producto con m2_id
			elif (material.material_id.uom_id.id == m2_id):
				material.quantity = self.total_cuadrados_manual

	@api.depends('secciones_ids', 'secciones_ids.ancho', 
				'secciones_ids.alto', 'secciones_ids.mts_cuadrados',
				'secciones_ids.unidades', 'secciones_ids.mts_cuadrados_sub')
	def _compute_total_secciones(self):
		for line in self:
			line.total_lineales = sum(line.secciones_ids.mapped('mts_lineales_sub'))
			line.total_cuadrados = sum(line.secciones_ids.mapped('mts_cuadrados_sub'))

class SaleOrderLineSecciones(models.Model):
	
	_name = 'sale.order.line.secciones'
	_order = 'order_line_id, sequence, id'

	@api.model
	def _get_default_seccion_name(self):
	
		for s in self.order_line_id.secciones_ids:
			val = dict(self._fields['seccion_name'].selection).get(s.seccion_name)
	
		return val

	order_line_id = fields.Many2one(
		comodel_name = 'sale.order.line',
		string = 'Order Line')

	sequence = fields.Integer(default = 10)

	ancho = fields.Float(
		string = 'Ancho',
		digits="Product Unit Of Measure")

	alto = fields.Float(
		string = 'Alto',
		digits="Product Unit Of Measure")

	mts_cuadrados = fields.Float(
		string = 'Mts. cuadrados',
		compute = '_compute_mts_cuadrados',
		readonly = True,
		digits="Product Unit Of Measure")

	seccion_name = fields.Selection(
		[('A','A'),
		('B','B'),
		('C','C'),
		('D','D'),
		('E','E'),
		('F','F'),
		('G','G'),
		('H','H'),
		('I','I'),
		('J','J'),
		('K','K')],
		string = 'Sección',
		default=_get_default_seccion_name,
		help = 'Seleccione sección...')

	unidades = fields.Integer(default = 1, string="Und.")

	mts_lineales_sub = fields.Float(
		string = "Mts. subtotal",
		compute = '_compute_mts_sub',
		readonly = True,
		digits="Product Unit Of Measure")

	mts_cuadrados_sub = fields.Float(
		string = 'Mts^2 subtotal',
		compute = '_compute_mts_sub',
		readonly = True,
		digits="Product Unit Of Measure")
	

	@api.depends('alto', 'ancho', 'unidades', 'mts_cuadrados')
	def _compute_mts_sub(self):
		for line in self:
			line.mts_cuadrados_sub = (line.unidades * line.mts_cuadrados)
			line.mts_lineales_sub = (line.unidades * line.ancho)

	@api.depends('ancho', 'alto')
	def _compute_mts_cuadrados(self):
		for line in self:
			line.mts_cuadrados = (line.ancho * line.alto)
"""
	@api.onchange('seccion_name')
	def _onchage_seccion_name(self):
		self.ancho = 0.0
		self.alto = 0.0
"""