# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class SaleOrder(models.Model):
	
	_inherit='sale.order'

	target_task_id = fields.Many2one('project.task', string="PT combinado")

	@api.multi
	def action_confirm(self):
		
		result = super(SaleOrder, self).action_confirm()
		self.merge_schedule_work()
		return result

	#Combina los PTs
	@api.multi
	def merge_schedule_work(self):
		if len(self.tasks_ids) > 1:
			#Obtenemos los valores para el PT resultante
			task_name = self.name + ':'
			for task in self.tasks_ids:
				task_name += '[%s] ' % task.sale_line_id.product_id.default_code

			values = {
				'name': '%s' % (task_name or ''),
				'project_id': self.project_project_id.id,
				'user_id': False,
				'description': self.merge_description(),
				'work_to_do': self.merge_work_to_do(),
				'planned_hours': self.merge_planned_hours(),
				'material_ids': self.merge_materials(),
				'timesheet_ids' : self.merge_timesheet(),
				'task_works_ids' : self.merge_task_works(),
			}

			#Creamos un PT nuevo 
			self.target_task_id = self.env['project.task'].create(values)

			#Combina los seguidores de los PTs seleccionados en el nuevo PT	
			self.target_task_id.message_subscribe(
				partner_ids=(self.tasks_ids - self.target_task_id).mapped('message_partner_ids').ids,
				channel_ids=(self.tasks_ids - self.target_task_id).mapped('message_channel_ids').ids,
			)

			#Combina los hilos de mensajes de los PTs seleccionados en el nuevo PT
			self.target_task_id.message_post_with_view(
				self.env.ref('project.mail_template_task_merge'),
				values={'target': True, 'tasks': self.tasks_ids - self.target_task_id},
				subtype_id=self.env.ref('mail.mt_comment').id
			)
			(self.tasks_ids - self.target_task_id).message_post_with_view(
				self.env.ref('project.mail_template_task_merge'),
				values={'target': False, 'task': self.target_task_id},
				subtype_id=self.env.ref('mail.mt_comment').id
			)
			(self.tasks_ids - self.target_task_id).write({'active': False})

	#Combina las descripciones de los PTs
	@api.multi
	def merge_description(self):
		return '<br/>'.join(self.tasks_ids.mapped(lambda task: "Descripción para el PT <b>%s</b>:<br/>%s" % (task.name, task.description or 'Sin descripción')))

	#Combina el trabajo a realizar de los PTs asociados
	@api.multi
	def merge_work_to_do(self):
		return '<br/>'.join(self.tasks_ids.mapped(lambda task: "Trabajo a realizar para el PT <b>%s</b>:<br/>%s" % (task.name, task.work_to_do or 'Sin trabajo a realizar')))

	#Combina las horas estimadas de los PTS asociados
	@api.multi
	def merge_planned_hours(self):
		hours = 0
		for task in self.tasks_ids:
			hours += task.planned_hours
		return hours

	#Combina la lista de materiales de los PTs asociados
	@api.multi
	def merge_materials(self):
		material_list = []
		for task in self.tasks_ids:
			if task.material_ids:
				for material in task.material_ids:
					if not material_list:
						material_list.append((0,0, {
							'product_id' : material.product_id.id,
							'quantity' : material.quantity
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
								'quantity' : material.quantity
								}))
	
		if material_list == []:
			material_list = False

		return material_list

	#Combina la lista de trabajos a realizar de los PTs asociados
	@api.multi
	def merge_task_works(self):
		works_list = []
		for task in self.tasks_ids:
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
	@api.multi
	def merge_timesheet(self):
		timesheet_list = []
		for task in self.tasks_ids:
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