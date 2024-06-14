# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProjectTaskConvert2Order(models.TransientModel):
	"""wizard to convert a Project task into a Order"""

	_name = "project.task.convert2order"
	_description = "Task convert to Order"

	@api.model
	def default_get(self, fields):
		result = super().default_get(fields)
		task_id = self.env.context.get("active_id")
		if task_id:
			result["task_id"] = task_id
		return result

	task_id = fields.Many2one(
		comodel_name="project.task", string="Tarea", 
	)
	product_id = fields.Many2one(
		comodel_name="product.product", string="Producto", required=True, 
	)

	def action_project_task_to(self):
		action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")

		if not self.task_id.partner_id:
			raise ValidationError(_('No existe ningún cliente asociado al PT.'))
		
		action['context'] = {
			'search_default_partner_id': self.task_id.partner_id.id,
			'default_partner_id': self.task_id.partner_id.id,
			'default_user_id': self.env.user.id,
			'default_company_id': self.task_id.company_id.id or self.env.company.id,
			#'default_tag_ids': [(6, 0, self.tag_ids.ids)]
		}
		if self.task_id.project_id:
			action['context']['default_project_id'] = self.task_id.project_id.id
		if self.task_id.analytic_account_id:
			action['context']['default_analytic_account_id'] = self.task_id.analytic_account_id.id
		if self.task_id.oppor_id:
			action['context']['default_opportunity_id'] = self.task_id.oppor_id.id
		if self.task_id.oppor_id.team_id:
			action['context']['default_team_id'] = self.task_id.oppor_id.team_id.id
		
		return action
