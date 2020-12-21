# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp



class SaleOrderLine(models.Model):

	_inherit='sale.order.line'


	#Calculo de los valores necesarios para crear el parte de trabajo correspondiente a la linea de pedido
	def _timesheet_create_task_prepare_values(self):
		self.ensure_one()
		project = self._timesheet_find_project()
		planned_hours = self._convert_qty_company_hours()

		work_list = []
		for work in self.task_works_ids:
			work_list.append((0,0, {
				'work_id' : work.work_id.id,
				'name' : work.name,
				'hours' : work.hours,
				}))

		material_list = []
		for material in self.task_materials_ids:
			material_list.append((0,0, {
				'product_id' : material.material_id.id,
				'quantity' : material.quantity,
				}))

		return {
			'name': '%s:%s' % (self.order_id.name or '', self.name.split(' ')[0] or self.product_id.name),
			'planned_hours': planned_hours,
			'remaining_hours': planned_hours,
			'partner_id': self.order_id.partner_id.id,
			'description': self.name + '<br/>',
			'work_to_do' : self.name + '<br/>',
			'project_id': project.id,
			'sale_line_id': self.id,
			'company_id': self.company_id.id,
			'email_from': self.order_id.partner_id.email,
			'user_id': False, # force non assigned task, as created as sudo()
			'material_ids': material_list,
			'task_works_ids': work_list,
			'oppor_id': self.order_id.opportunity_id.id or False, # Asocia con el aviso
			}

	