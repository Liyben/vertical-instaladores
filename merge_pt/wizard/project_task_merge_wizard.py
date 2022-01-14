# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ProjectTaskMergeWizard(models.TransientModel):
	_name = 'project.task.merge.wizard'

	task_ids = fields.Many2many('project.task', string="Tareas a combinar", required=True)
	user_id = fields.Many2one('res.users', string="Asignada a")
	create_new_task = fields.Boolean('Crear una nueva tarea')
	target_task_name = fields.Char('Nuevo nombre de tarea')
	target_project_id = fields.Many2one('project.project', string="Proyecto meta")
	target_task_id = fields.Many2one('project.task', string="Combinar en una tarea existente")
	
	#Combina los PTs
	def merge_tasks(self):
		#Obtenemos los valores para el PT resultante
		values = {
		'user_id': self.user_id.id,
		'work_to_do': self.merge_work_to_do(),
		'planned_hours': self.merge_planned_hours(),
		'material_ids': self.merge_materials(),
		'timesheet_ids' : self.merge_timesheet(),
		'task_works_ids' : self.merge_task_works(),
		}

		#Creamos un PT nuevo o sobrescribimos uno ya realizado
		if self.create_new_task:
			values.update({
				'name': self.target_task_name,
				'project_id': self.target_project_id.id
				})
			self.target_task_id = self.env['project.task'].create(values)
		else:
			self.target_task_id.material_ids = False
			self.target_task_id.timesheet_ids = False
			self.target_task_id.task_works_ids = False
			self.target_task_id.write(values)

		#Combina los seguidores de los PTs seleccionados en el PT resultante
		self.merge_followers()

		#Combina los hilos de mensajes de los PTs seleccionados en el PT resultante
		self.target_task_id.message_post_with_view(
			'project.mail_template_task_merge',
			values={'target': True, 'tasks': self.task_ids - self.target_task_id},
			subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')
		)
		(self.task_ids - self.target_task_id).message_post_with_view(
			'project.mail_template_task_merge',
			values={'target': False, 'task': self.target_task_id},
			subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')
		)
		(self.task_ids - self.target_task_id).write({'active': False})

		#Muestra el PT resultante en su vista formulario
		return {
		"type": "ir.actions.act_window",
		"res_model": "project.task",
		"views": [[False, "form"]],
		"res_id": self.target_task_id.id,
		}

	#Combina los seguidores de los PTs seleccionados
	def merge_followers(self):
		self.target_task_id.message_subscribe(
			partner_ids=(self.task_ids - self.target_task_id).mapped('message_partner_ids').ids,
			channel_ids=(self.task_ids - self.target_task_id).mapped('message_channel_ids').ids,
		)

	#Combina el trabajo a realiza de los PTs seleccionados
	def merge_work_to_do(self):
		return '<br/>'.join(self.task_ids.mapped(lambda task: "Trabajo a realizar para el PT <b>%s</b>:<br/>%s" % (task.name, task.work_to_do or 'Sin trabajo a realizar')))

	#Combina las horas estimadas de los PTS seleccionados
	def merge_planned_hours(self):
		hours = 0
		for task in self.task_ids:
			hours += task.planned_hours
		return hours

	#Combina la lista de materiales de los PTs seleccionados
	def merge_materials(self):
		material_list = []
		for task in self.task_ids:
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

	#Combina la lista de trabajos a realizar de los PTs seleccionados
	def merge_task_works(self):
		works_list = []
		for task in self.task_ids:
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

	#Combina los parte de horas de los PTs seleccionados
	def merge_timesheet(self):
		timesheet_list = []
		for task in self.task_ids:
			if task.timesheet_ids:
				for timesheet in task.timesheet_ids:
					timesheet_list.append((0,0, {
						'date_time' : timesheet.date_time,
						'name' : timesheet.name,
						'employee_id' : timesheet.employee_id.id,
						'unit_amount' : timesheet.unit_amount,
						'account_id' : timesheet.account_id.id
						}))

		if timesheet_list == []:
			timesheet_list = False

		return timesheet_list

	@api.model
	def default_get(self, fields):
		result = super(ProjectTaskMergeWizard, self).default_get(fields)
		selected_tasks = self.env['project.task'].browse(self.env.context.get('active_ids', False))
		assigned_tasks = selected_tasks.filtered(lambda task: task.user_id)
		result.update({
			'task_ids': selected_tasks.ids,
			'user_id': assigned_tasks and assigned_tasks[0].user_id.id or False,
			'target_project_id': selected_tasks[0].project_id.id,
			'target_task_id': selected_tasks[0].id
		})
		return result
