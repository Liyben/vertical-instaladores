# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import html2text

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
	
	def _get_sale_line_data(self, sale_order):
		self.ensure_one()
		res = {
			"product_id": self.product_id.id,
			"product_uom_qty": 1.0,
			"order_id": sale_order.id,
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

		order_line_model = self.env["sale.order.line"].sudo()
		sale_order_line_data = self._get_sale_line_data(sale_order)
		sale_order_line = order_line_model.create(sale_order_line_data)
		sale_order_line.product_id_change()

		if sale_order_line:
			self.task_id.sale_line_id = sale_order_line.id
		#Calculamos la nueva lista de materiales que le pasaremos a la linea de pedido asociada
			material_list = []
			if self.task_id.material_ids:
				for material in self.task_id.material_ids:
					mat = material.product_id.with_context(
							lang=sale_order.partner_id.lang,
							partner=sale_order.partner_id.id,
							quantity=material.quantity,
							date=sale_order.date_order,
							pricelist=sale_order.pricelist_id.id,
							uom=material.product_id.uom_id.id)

					material_list.append((0,0, {
						'material_id' : material.product_id.id,
						'name' : material.product_id.name,
						'quantity' : material.quantity,
						'sale_price_unit' : sale_order.env['account.tax']._fix_tax_included_price_company(sale_order_line._get_display_price_line(mat, material.product_id, material.quantity), mat.taxes_id, sale_order_line.tax_id, sale_order_line.company_id),
						'cost_price_unit' : material.product_id.standard_price,
						'discount' : sale_order_line._get_discount_line(material.product_id, material.quantity) or 0.0
						}))
			else:
				material_list = False

			#Calculamos la nueva lista de trabajos que le pasaremos a la linea de pedido asociada
			work_list = []
			if self.task_id.timesheet_ids:
				for work in self.task_id.timesheet_ids:
					sale_work = 0
					cost_work = 0
					if work.employee_id.work_id:
						workforce = work.employee_id.work_id.with_context(
							lang=sale_order.partner_id.lang,
							partner=sale_order.partner_id.id,
							quantity=work.unit_amount,
							date=sale_order.date_order,
							pricelist=sale_order.pricelist_id.id,
							uom=work.employee_id.work_id.uom_id.id)

						sale_work = sale_order.env['account.tax']._fix_tax_included_price_company(sale_order_line._get_display_price_line(workforce, work.employee_id.work_id, work.unit_amount), workforce.taxes_id, sale_order_line.tax_id, sale_order_line.company_id)
						cost_work = work.employee_id.work_id.standard_price
					
					work_list.append((0,0, {
							'name' : work.name,
							'work_id': work.employee_id.work_id.id,
							'hours' : work.unit_amount,
							'sale_price_unit' : sale_work,
							'cost_price_unit' : cost_work,
							'discount' : sale_order_line._get_discount_line(work.employee_id.work_id, work.unit_amount) or 0.0
						}))
			else:
				work_list = False

			#Calculamos la nueva descripción de la linea de pedido asociada
			nameToText = ''
			if self.task_id.code:
				nameToText += 'Parte de Trabajo: ' + self.task_id.code + '<br/>'

			if self.task_id.work_to_do:
				nameToText += self.task_id.work_to_do + '<br/>'

			#Limpiamos la lista de trabajos y materiales de la linea de pedido asociada
			sale_order_line.update({'task_works_ids' : False,
								'task_materials_ids' : False
								})

			#Actualizamos con las nuevas listas de trabajos y materiales de la linea de pedido asociada
			sale_order_line.update({'task_works_ids' : work_list,
								'task_materials_ids' : material_list,
								'name' : html2text.html2text(nameToText),
								})

			#Actualizamos los precios de venta y coste de la linea de pedido asociada
			for line in sale_order_line:
				line.price_unit = (line.total_sp_material + line.total_sp_work)
				line.purchase_price = (line.total_cp_material + line.total_cp_work)
					
		action["res_id"] = sale_order.id

		return action
