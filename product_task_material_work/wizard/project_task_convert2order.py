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

	def action_project_task_to(self):
		action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
		action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
		
		if not self.task_id.partner_id:
			raise ValidationError(_('No existe ningún cliente asociado al PT.'))
		
		order_line = []
		if self.task_id:
			material_list = []
			work_list = []
			auto_create_task = False
			product = self.product_id
			if product:
				auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_in_project')
			
			if auto_create_task:
				for work in self.task_id.material_ids:
					work_list.append((0,0, {
						'name' : work.name,
						'work_id': work.work_id.id,
						'sale_price_unit' : work.sale_price_unit,
						'cost_price_unit' : work.cost_price_unit,
						'hours' : work.hours,
						}))
				
				for material in self.task_id.material_ids:
					material_list.append((0,0, {
						'material_id' : material.material_id.id,
						'name' : material.name,
						'sale_price_unit' : material.sale_price_unit,
						'cost_price_unit' : material.cost_price_unit,
						'quantity' : material.quantity,
						}))

				order_line.append((0,0,{'product_id': self.product_id.id,
					'name': self.task_id.work_to_do,
					'product_uom_qty':1.0,
					#'product_uom': self.product_id.product_uom.id,
					#'price_unit': line.price_unit,
					#'purchase_price': line.cost_unit,
					#'tax_id':[(6, 0, line.tax_id.ids)],
					#'task_works_ids' : work_list,
					#'task_materials_ids' : material_list,
					#'auto_create_task' : auto_create_task, 
					'task_id': self.task_id.id, 
					}))
		else:
			order_line = False

		action['context'] = {
			#'search_default_partner_id': self.task_id.partner_id.id,
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
		if order_line:
			action['context']['default_order_line'] = order_line

		return action
