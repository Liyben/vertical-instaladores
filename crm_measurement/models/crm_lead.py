# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class CrmLeadProductLine(models.Model):

	_name = 'crm.lead.product.line'
	_order = 'crm_lead_id, sequence, id'
	
	sequence = fields.Integer()
	product_id = fields.Many2one(
		'product.product', string='Producto', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
		required=True, change_default=True, ondelete='restrict', check_company=True)
	name = fields.Text(string='Descripción', required=True)
	product_uom_qty = fields.Float(string='Cantidad', digits='Product Unit of Measure', required=True, default=1.0)
	product_uom = fields.Many2one('uom.uom', string='Unidad de medida', domain="[('category_id', '=', product_uom_category_id)]")
	product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
	price_unit = fields.Float('Precio unidad', required=True, digits='Product Price', default=0.0)
	tax_id = fields.Many2many('account.tax', string='Impuestos', context={'active_test': False})
	company_id = fields.Many2one('res.company', 'Compañia', required=True, index=True, default=lambda self: self.env.company)
	crm_lead_id = fields.Many2one('crm.lead')
	
	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.name = self.product_id.get_product_multiline_description_sale()
			self.price_unit = self.product_id.lst_price
			self.product_uom = self.product_id.uom_id.id
			self.tax_id = self.product_id.taxes_id.ids

class CrmLeadSections(models.Model):
	
	_name = 'crm.lead.section.line'
	_order = 'crm_lead_id, sequence, id'

	crm_lead_id = fields.Many2one(
		comodel_name = 'crm.lead',
		)

	sequence = fields.Integer()

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

	section_name = fields.Selection(
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


class CrmLead(models.Model):
	_inherit = 'crm.lead'

	section_ids = fields.One2many(
		comodel_name = 'crm.lead.section.line',
		inverse_name = 'crm_lead_id',
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

	last_section_name = fields.Char(string="Ultima sección",compute = '_compute_last_section_name',store=True)

	product_ids = fields.One2many(
		comodel_name = 'crm.lead.product.line',
		inverse_name = 'crm_lead_id',
		string = 'Productos')
	
	@api.depends('section_ids', 'section_ids.ancho', 
				'section_ids.alto', 'section_ids.mts_cuadrados',
				'section_ids.unidades', 'section_ids.mts_cuadrados_sub')
	def _compute_total_secciones(self):
		for line in self:
			line.total_lineales = sum(line.section_ids.mapped('mts_lineales_sub'))
			line.total_cuadrados = sum(line.section_ids.mapped('mts_cuadrados_sub'))

	@api.depends('section_ids','section_ids.section_name')
	def _compute_last_section_name(self):
		for line in self:
			if len(line.section_ids) == 0:
				line.last_section_name = 'A'
			else:
				s_name = line.section_ids[len(line.section_ids)-1].section_name
				
				if s_name == 'A':
					line.last_section_name = 'B'
				elif s_name == 'B':
					line.last_section_name = 'C'
				elif s_name == 'C':
					line.last_section_name = 'D'
				elif s_name == 'D':
					line.last_section_name = 'E'
				elif s_name == 'E':
					line.last_section_name = 'F'
				elif s_name == 'F':
					line.last_section_name = 'G'
				elif s_name == 'G':
					line.last_section_name = 'H'
				elif s_name == 'H':
					line.last_section_name = 'I'
				elif s_name == 'I':
					line.last_section_name = 'J'
				elif s_name == 'J':
					line.last_section_name = 'K'
				elif s_name == 'K':
					line.last_section_name = 'A'
				else: 
					line.last_section_name = 'A'
			
	def action_new_quotation(self):
		action = super(CrmLead, self).action_new_quotation()
		if self.product_ids:
			order_lines = []
			for line in self.product_ids:
				order_lines.append((0,0,{'product_id': line.product_id.id,
				'name': line.name,
				'product_uom_qty':line.product_uom_qty,
				'product_uom': line.product_uom.id,
				'price_unit': line.price_unit,
				'tax_id':[(6, 0, line.tax_id.ids)],
				'secciones_ids':[(6, 0, line.crm_lead_id.section_ids.ids)],
				'manual_mode':line.crm_lead_id.manual_mode,
				'total_lineales_manual':line.crm_lead_id.total_lineales_manual,
				'total_cuadrados_manual':line.crm_lead_id.total_cuadrados_manual,
				'last_seccion_name':line.crm_lead_id.last_seccion_name
				}))

			if order_lines:
				action['context']['default_order_line'] = self.order_lines
			
		return action	
