# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	#Mano de obra asociada al empleado
	work_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', required=False)

	#Carga el coste hora en el empleado
	@api.onchange('work_id')
	def _onchange_work_id(self):
		for record in self:
			record.timesheet_cost = record.work_id.standard_price


class HrEmployee(models.Model):
	_inherit = 'hr.employee.public'

	#Mano de obra asociada al empleado
	work_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', required=False)