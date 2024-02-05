# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, exceptions, _

class Task(models.Model):
	
	_inherit='project.task'

	merged_parent_id = fields.Many2one('project.task', string='Tarea destino', index=True)
	merged_child_ids = fields.One2many('project.task', 'merged_parent_id', string="Tareas origen", context={'active_test': False})


	def unlink(self):
		for task in self.merged_child_ids:
			if task.sale_line_id:
				task.sale_line_id = False
			task.unlink()
			
		return super(Task, self).unlink()
	