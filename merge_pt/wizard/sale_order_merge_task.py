# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderMergeTaskWizard(models.TransientModel):
	_name = 'sale.order.merge.task.wizard'
	_description = "Combinar partes de trabajo desde presupuesto"

	target_task_id = fields.Many2one('project.task', string="PT fusionado")

	#Combina los PTs
	def merge_task(self):
		
		#Obtenemos el presupuesto activo
		order_ids = self.env['sale.order'].browse(self.env.context.get('active_ids', False))
		order_selected = order_ids[0]
		#Comprobamos el control de facturación de los productos compuestos
		list_bool = []
		for line in order_selected.order_line:
			if line.auto_create_task:
				list_bool.append(line.product_id.invoicing_finished_task)
		if any(list_bool) == True and all(list_bool) == False:
			raise UserError(_('Para combinar partes de trabajo todos deben de tener el mismo control de facturas.\n'+
			'Atención: ¡El sistema ha creado las tareas correspondientes a cada linea de presuesto. Si desea unificar todas las tareas, siga estos pasos:\n'+
			'1. Cancelar presupuesto.\n'+
			'2. Configurar todos los productos con el mismo control de factura.\n'+
			'3. Vuelva al prespuesto, conviertalo a presupuesto y confirmelo.\n'))

		#Obtenemos los valores para el PT resultante
		task_name = order_selected.name + ':'
		for task in order_selected.tasks_ids:
			task_name += '[%s] ' % task.sale_line_id.product_id.default_code

		values = {
			'name': '%s' % (task_name or ''),
			'project_id': order_selected.tasks_ids[0].project_id.id,
			'user_id': False,
			'work_to_do': self.merge_work_to_do(order_selected),
			'planned_hours': self.merge_planned_hours(order_selected),
			'material_ids': self.merge_materials(order_selected),
			'timesheet_ids' : self.merge_timesheet(order_selected),
			'task_works_ids' : self.merge_task_works(order_selected),
		}

		#Creamos un PT nuevo 
		self.target_task_id = self.env['project.task'].create(values)

		#Asignamos a las tareas del presupuesto la tarea destino
		for task in (order_selected.tasks_ids - self.target_task_id):
			task.merged_parent_id = self.target_task_id.id

		#Combina los seguidores de los PTs seleccionados en el nuevo PT	
		self.target_task_id.message_subscribe(
			partner_ids=(order_selected.tasks_ids - self.target_task_id).mapped('message_partner_ids').ids,
			channel_ids=(order_selected.tasks_ids - self.target_task_id).mapped('message_channel_ids').ids,
		)

		#Combina los hilos de mensajes de los PTs seleccionados en el nuevo PT
		self.target_task_id.message_post_with_view(
			self.env.ref('merge_pt.mail_template_task_merge'),
			values={'target': True, 'tasks': order_selected.tasks_ids - self.target_task_id},
			subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')
		)
		(order_selected.tasks_ids - self.target_task_id).message_post_with_view(
			self.env.ref('merge_pt.mail_template_task_merge'),
			values={'target': False, 'task': self.target_task_id},
			subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')
		)
		(order_selected.tasks_ids - self.target_task_id).write({'active': False})

	#Combina el trabajo a realizar de los PTs asociados
	def merge_work_to_do(self, order):
		return '<br/>'.join(order.tasks_ids.mapped(lambda task: "Trabajo a realizar para el PT <b>%s</b>:<br/>%s" % (task.name, task.work_to_do or 'Sin trabajo a realizar')))

	#Combina las horas estimadas de los PTS asociados
	def merge_planned_hours(self, order):
		hours = 0
		for task in order.tasks_ids:
			hours += task.planned_hours
		return hours

	#Combina la lista de materiales de los PTs asociados
	def merge_materials(self, order):
		material_list = []
		for task in order.tasks_ids:
			if task.material_ids:
				for material in task.material_ids:
					if not material_list:
						material_list.append((0,0, {
							'product_id' : material.product_id.id,
							'quantity' : material.quantity,
							'product_uom_id' : material.product_uom_id
						}))
					else:
						encontrado = False
						for item in material_list:
							material_id = item[2]["product_id"]
							if material_id == material.product_id.id:
								item[2]["quantity"] = item[2]["quantity"] + material.quantity
								encontrado = True
						if not encontrado:
							material_list.append((0,0, {
								'product_id' : material.product_id.id,
								'quantity' : material.quantity,
								'product_uom_id' : material.product_uom_id
								}))
	
		if material_list == []:
			material_list = False

		return material_list

	#Combina la lista de trabajos a realizar de los PTs asociados
	def merge_task_works(self, order):
		works_list = []
		for task in order.tasks_ids:
			if task.task_works_ids:
				for work in task.task_works_ids:
					works_list.append((0,0, {
						'work_id' : work.work_id.id,
						'name' : work.name,
						'hours' : work.hours
						}))
		if works_list == []:
			works_list = False

		return works_list

	#Combina los parte de horas de los PTs asociados
	def merge_timesheet(self, order):
		timesheet_list = []
		for task in order.tasks_ids:
			if task.timesheet_ids:
				for timesheet in task.timesheet_ids:
					timesheet_list.append((0,0, {
						'date' : timesheet.date,
						'name' : timesheet.name,
						'employee_id' : timesheet.employee_id.id,
						'unit_amount' : timesheet.unit_amount,
						'account_id' : timesheet.account_id.id
						}))

		if timesheet_list == []:
			timesheet_list = False

		return timesheet_list