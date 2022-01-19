# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, exceptions, _

class SaleOrder(models.Model):
	
	_inherit='sale.order'

	def action_confirm(self):
		result = super(SaleOrder, self).action_confirm()
		self.merge_task_wizard_open()
		return result

	def merge_task_wizard_open(self):
		return self.env["ir.actions.act_window"]._for_xml_id("merge_pt.action_view_sale_order_merge_task")
