# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, exceptions, _

class SaleOrder(models.Model):
	
	_inherit='sale.order'

	def merge_task_action_confirm(self):
		self.action_confirm()
		if len(self.tasks_ids) > 1:
			return {'type': 'ir.actions.act_window',
				'name': _('Combinar partes de trabajo'),
				'res_model': 'sale.order.merge.task.wizard',
				'target': 'new',
				'view_id': self.env.ref('merge_pt.view_sale_order_merge_task').id,
				'view_mode': 'form'}

	"""
	def merge_task_wizard_open(self):
		return self.env["ir.actions.act_window"]._for_xml_id("merge_pt.action_view_sale_order_merge_task")
	"""

