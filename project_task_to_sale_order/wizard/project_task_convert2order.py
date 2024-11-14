# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProjectTaskConvert2Order(models.TransientModel):
	"""wizard to convert a Project task into a Order"""

	_name = "project.task.convert2order"
	_description = "Task convert to Order"

	task_id = fields.Many2one(
		comodel_name="project.task", string="Tarea", default=lambda self: self.env.context.get('active_id')
	)
	product_id = fields.Many2one(
		comodel_name="product.product", string="Producto", required=True, domain="[('auto_create_task', '=', True]"
	)

	def _get_sale_order_data(self):
		self.ensure_one()
		res = {
			"partner_id": self.task_id.partner_id.id,
			"partner_invoice_id": self.task_id.partner_id.address_get(['invoice'])['invoice'] if self.task_id.partner_id else False,
            "partner_shipping_id": self.task_id.partner_id.address_get(['delivery'])['delivery'] if self.task_id.partner_id else False,
			"pricelist_id": self.task_id.partner_id.property_product_pricelist and self.task_id.partner_id.property_product_pricelist.id,
            "payment_term_id": self.task_id.partner_id.property_payment_term_id and self.task_id.partner_id.property_payment_term_id.id,
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

		order_line_model = self.env["sale.order.line"].sudo()
		sale_order_line_data = self._get_sale_line_data(sale_order)
		sale_order_line = order_line_model.create(sale_order_line_data)
		#sale_order_line.product_id_change()

		if sale_order_line:
			self.task_id.sale_line_id = sale_order_line.id
		#Calculamos la nueva lista de materiales que le pasaremos a la linea de pedido asociada
			material_list = []
			if self.task_id.material_ids:
				for move in self.task_id.move_ids:
					material_list.append((0,0, {
						'material_id' : move.product_id.id,
						'name' : move.name,
						'quantity' : move.product_uom_qty,
						'sale_price_unit' : move.product_id.list_price,
						'cost_price_unit' : move.product_id.standard_price,
						'discount' : 0.0
						}))
			else:
				material_list = False

			#Calculamos la nueva lista de trabajos que le pasaremos a la linea de pedido asociada
			work_list = []
			if self.task_id.timesheet_ids:
				for work in self.task_id.timesheet_ids:					
					work_list.append((0,0, {
							'name' : work.name,
							'work_id': work.employee_id.work_id.id,
							'hours' : work.unit_amount,
							'sale_price_unit' : work.employee_id.work_id.standard_price if work.employee_id.work_id else 0.0,
							'cost_price_unit' : work.employee_id.work_id.standard_price if work.employee_id.work_id else 0.0,
							'discount' : 0.0
						}))
			else:
				work_list = False

			#Calculamos la nueva descripción de la linea de pedido asociada
			nameToText = 'Parte de Trabajo: ' + self.task_id.name + '<br/>'

			if self.task_id.work_to_do:
				nameToText += self.task_id.work_to_do + '<br/>'

			#Limpiamos la lista de trabajos y materiales de la linea de pedido asociada
			sale_order_line.update({'task_works_ids' : False,
								'task_materials_ids' : False
								})

			#Actualizamos con las nuevas listas de trabajos y materiales de la linea de pedido asociada
			sale_order_line.update({'task_works_ids' : work_list,
								'task_materials_ids' : material_list,
								'name' : nameToText,
								'task_id' : self.task_id.id,
								})
					
		action["res_id"] = sale_order.id

		return action
