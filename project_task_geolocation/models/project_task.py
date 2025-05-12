# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
	_inherit = 'project.task'

	view_button_start = fields.Boolean(string='Ver boton comienzo', compute='_compute_view_button_start', store=True)
	view_button_stop = fields.Boolean(string='Ver boton comienzo', compute='_compute_view_button_stop', store=True)

	def _compute_view_button_start(self):
		for record in self:
			if self.env.user:
				employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('company_id', '=', self.env.company.id)])
				if employee:
					now = fields.Datetime.now()
					attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_in', '<=', now), ('check_out', '=', False)], order="check_in desc", limit=1)
					if attendance:
						aal = self.env['account.analytic.line'].search([('attendance_id', '=', attendance.id), ('employee_id', '=', employee.id)])
						if aal:
							record.view_button_start = False
						else:
							record.view_button_start = True
					else:
						record.view_button_start = False
				else:
					record.view_button_start = False
			else:
				record.view_button_start = False
		
	def _compute_view_button_stop(self):
		for record in self:
			if self.env.user:
				employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('company_id', '=', self.env.company.id)])
				if employee:
					now = fields.Datetime.now()
					attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_in', '<=', now), ('check_out', '=', False)], order="check_in desc", limit=1)
					if attendance:
						aal = self.env['account.analytic.line'].search([('attendance_id', '=', attendance.id), ('employee_id', '=', employee.id), ('task_id', '=', record.id)])
						if aal:
							record.view_button_stop = True
						else:
							record.view_button_stop = False
					else:
						record.view_button_stop = False
				else:
					record.view_button_stop = False
			else:
				record.view_button_stop = False
