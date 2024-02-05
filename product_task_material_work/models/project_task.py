# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import html2text

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp

class ProjectTask(models.Model):
	_inherit = 'project.task'

	#Indica si un PT es facturable por administracion o no
	by_administration = fields.Boolean(string='Por Administración', default=False)

	#Campo relacional para los trabajos de la linea de presupuesto
	task_works_ids = fields.One2many(comodel_name='project.task.work', inverse_name='project_task_id', string='Trabajos', copy=True)

	#Trabajo a realizar
	work_to_do = fields.Html(string='Trabajo a realizar')

	#Opportunidad / Aviso
	oppor_id = fields.Many2one(comodel_name='crm.lead', string='Oportunidad / Aviso')

	#Firma digital
	signature = fields.Binary(string='Firma')
	sign_by = fields.Char(string='Firmado por')

	@api.model
	def create(self, vals):
		task = super(ProjectTask, self).create(vals)
		if task.signature:
			values = {'signature': task.signature}
			task._track_signature(vals, 'signature')
		return task
	
	def write(self, vals):
		self._track_signature(vals, 'signature')
		return super(ProjectTask, self).write(vals)
		
	#Al pasar un PT a por administracion recalculamos su linea de pedido asociada
	#con los cambios introducidos en el PT
	
	def sale_order_action_recalculate(self):
		self._check_sale_line_exist() #Comprobamos si existe linea de pedido asociada
		self._check_sale_line_state() #Comprobamos en que estado se encuentra
		if self.task_to_invoice:
			#Calculamos la nueva lista de materiales que le pasaremos a la linea de pedido asociada
			material_list = []
			if self.material_ids:
				for material in self.material_ids:
					mat = material.product_id.with_context(
							lang=self.sale_line_id.order_id.partner_id.lang,
							partner=self.sale_line_id.order_id.partner_id.id,
							quantity=material.quantity,
							date=self.sale_line_id.order_id.date_order,
							pricelist=self.sale_line_id.order_id.pricelist_id.id,
							uom=material.product_id.uom_id.id)

					material_list.append((0,0, {
						'material_id' : material.product_id.id,
						'name' : material.product_id.name,
						'quantity' : material.quantity,
						'sale_price_unit' : self.sale_line_id.order_id.env['account.tax']._fix_tax_included_price_company(self.sale_line_id._get_display_price_line(mat, material.product_id, material.quantity), mat.taxes_id, self.sale_line_id.tax_id, self.sale_line_id.company_id),
						'cost_price_unit' : material.product_id.standard_price,
						'discount' : self.sale_line_id._get_discount_line(material.product_id, material.quantity) or 0.0
						}))
			else:
				material_list = False

			#Calculamos los precios de venta y coste unitarios para las lineas de trabajos
			#a partir de la mano de obra de la linea de pedido asociada
			#sale_work = 0
			#cost_work = 0
			#if self.sale_line_id.workforce_id:
			#	sale_work = self.sale_line_id.workforce_id.list_price
			#	cost_work = self.sale_line_id.workforce_id.standard_price

			#Calculamos la nueva lista de trabajos que le pasaremos a la linea de pedido asociada
			work_list = []
			if self.timesheet_ids:
				for work in self.timesheet_ids:
					sale_work = 0
					cost_work = 0
					if work.employee_id.work_id:
						workforce = work.employee_id.work_id.with_context(
							lang=self.sale_line_id.order_id.partner_id.lang,
							partner=self.sale_line_id.order_id.partner_id.id,
							quantity=work.unit_amount,
							date=self.sale_line_id.order_id.date_order,
							pricelist=self.sale_line_id.order_id.pricelist_id.id,
							uom=work.employee_id.work_id.uom_id.id)

						sale_work = self.sale_line_id.order_id.env['account.tax']._fix_tax_included_price_company(self.sale_line_id._get_display_price_line(workforce, work.employee_id.work_id, work.unit_amount), workforce.taxes_id, self.sale_line_id.tax_id, self.sale_line_id.company_id)
						cost_work = work.employee_id.work_id.standard_price
					
					work_list.append((0,0, {
							'name' : work.name,
							'work_id': work.employee_id.work_id.id,
							'hours' : work.unit_amount,
							'sale_price_unit' : sale_work,
							'cost_price_unit' : cost_work,
							'discount' : self.sale_line_id._get_discount_line(work.employee_id.work_id, work.unit_amount) or 0.0
						}))
			else:
				work_list = False

			#Calculamos la nueva descripción de la linea de pedido asociada
			nameToText = ''
			#if self.oppor_id.sequence_code:
			#	nameToText = 'Aviso: ' + self.oppor_id.sequence_code + ', '

			if self.code:
				nameToText += 'Parte de Trabajo: ' + self.code + '<br/>'

			if self.work_to_do:
				nameToText += self.work_to_do + '<br/>'

			#Limpiamos la lista de trabajos y materiales de la linea de pedido asociada
			self.sale_line_id.update({'task_works_ids' : False,
								'task_materials_ids' : False
								})

			#Actualizamos con las nuevas listas de trabajos y materiales de la linea de pedido asociada
			self.sale_line_id.update({'task_works_ids' : work_list,
								'task_materials_ids' : material_list,
								'name' : html2text.html2text(nameToText)
								})

			#Actualizamos los precios de venta y coste de la linea de pedido asociada
			for line in self.sale_line_id:
				line.price_unit = (line.total_sp_material + line.total_sp_work)
				line.purchase_price = (line.total_cp_material + line.total_cp_work)

			#Cambiamos el valor del campo Por Administracio del PT
			if not self.by_administration:
				self.by_administration = not self.by_administration

	#Funcion que comprueba si el PT tiene linea de pedido
	def _check_sale_line_exist(self):
		if not self.sale_line_id:
			raise ValidationError(_('No existe ninguna linea de pedido asociada al PT.'))

	#Comprobamos el estado de la linea de pedido, en el caso que no cumpla los requisitos necesarios
	#para ser facturada, se lanza una excepcion que avisa al usuario con un mensaje
	def _check_sale_line_state(self, sale_line_id=False):
		sale_lines = self.mapped('sale_line_id')
		if sale_line_id:
			sale_lines |= self.env['sale.order.line'].browse(sale_line_id)
		for sale_line in sale_lines:
			#Comprobamos la cantidad de la linea de pedido
			if sale_line.product_uom_qty == 0:
				raise ValidationError(_('No puede crear/modificar un PT relacionado con '
					'una cantidad en la linea de pedido igual a 0. Compruebe las lineas de pedido.'))
			#Comprobamos el estado de la linea de pedido
			if (sale_line.state in ('done', 'cancel') or 
				sale_line.invoice_status == 'invoiced'): 
				raise ValidationError(_('No puede crear/modificar un PT relacionado con '
					'una linea de pedido facturada, realizada o cancelada'))

	
class ProjectTaskMaterial(models.Model):
	_inherit = "project.task.material"

	product_uom_id = fields.Many2one(comodel_name="uom.uom", string="Unit of Measure")
	
class ProjectTaskWork(models.Model):
	"""Modelo para almacenar los trabajos de la linea de pedido en el parte de trabajo"""

	_name = 'project.task.work'
	_description = 'Trabajos en el parte de trabajo'
	_order = 'project_task_id, sequence, id'

	#Campo relación con el parte de trabajo
	project_task_id = fields.Many2one(comodel_name='project.task', string='Parte de trabajo', ondelete='cascade')
	#Mano de obra
	work_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', required=True)
	#Descripcion del trabajo
	name = fields.Char(string='Nombre', required=True)
	#Horas empleadas en el trabajo
	hours = fields.Float(string='Horas')
	#Secuencia
	sequence = fields.Integer()
	#Indica si esta realizado por el tecnico
	to_done = fields.Boolean(string='Realizado', default=False)
	#Indica si esta validado
	validated = fields.Boolean(string='Validado', default=False)

	#Carga el nombre de la mano de obra
	@api.onchange('work_id')
	def _onchange_work_id(self):
		for record in self:
			record.name = record.work_id.name