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
		comodel_name="product.product", string="Producto", required=True, domain="[('service_tracking', 'in', ['task_global_project', 'task_in_project'])]"
	)

	def _get_sale_order_data(self):
		self.ensure_one()
		res = {
			"partner_id": self.task_id.partner_id.id,
			"analytic_account_id": self.task_id.analytic_account_id.id or False,
			"project_id": self.task_id.project_id.id or False,
			"opportunity_id": self.task_id.oppor_id.id or False,
			"team_id": self.task_id.oppor_id.team_id.id or False,
			"user_id": self.env.user.id,
			"company_id": self.task_id.company_id.id or self.env.company.id,
		}
		return res
	
	def action_project_task_to(self):

		if not self.task_id.partner_id:
			raise ValidationError(_('No existe ningún cliente asociado al PT.'))
		
		action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations")
		action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
		
		order_model = self.env["sale.order"].sudo()
		sale_order_data = self._get_sale_order_data()
		sale_order = order_model.create(sale_order_data)
		sale_order.onchange_partner_id()
	
		action["res_id"] = sale_order.id

		return action
