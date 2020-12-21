# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp

class SaleOrder(models.Model):
	"""docstring for SaleOrder"""
	_inherit='sale.order'

	@api.multi
	def action_confirm(self):
		
		result = super(SaleOrder, self).action_confirm()
		for order in self:
			if order.opportunity_id:
				order.opportunity_id.project_id = order.project_project_id.id
				order.opportunity_id.parent_analytic_account_id = order.parent_analytic_account_id.id
				for task in order.opportunity_id.task_ids:
					if not task.sale_line_id:
						task.project_id = order.project_project_id.id
				#ir_model_data = self.env['ir.model.data']
				#try:
				#	stage_id = ir_model_data.get_object_reference('crm','stage_lead4')[1]
				#except ValueError:
				#	stage_id = False
				order.opportunity_id.stage_id = self.env.ref('crm.stage_lead4', raise_if_not_found=False).id
		return result
