# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, exceptions, _

class Task(models.Model):
	
	_inherit='project.task'


	def toggle_invoiceable(self):
		for task in self.merged_child_ids:
			task.toggle_invoiceable()
			line = task.mapped("sale_line_id")
			if (
				line.product_id.type == "service"
				and line.product_id.invoicing_finished_task
				and line.product_id.service_tracking in ["task_global_project", "task_in_project"]
				and not task.invoiceable
			):
				line.update({"qty_to_invoice": 0.0})
			line._get_to_invoice_qty()
		return super(Task, self).toggle_invoiceable()