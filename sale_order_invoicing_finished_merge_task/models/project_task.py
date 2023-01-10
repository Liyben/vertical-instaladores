# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, exceptions, _

class Task(models.Model):
	
	_inherit='project.task'


	def toggle_invoiceable(self):
		for task in self.merged_child_ids:
			task.toggle_invoiceable()
			task.mapped("sale_line_id")._compute_qty_delivered()
		
		return super(Task, self).toggle_invoiceable()