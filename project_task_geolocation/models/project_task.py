# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
	_inherit = 'project.task'

	view_button_start = fields.Boolean(string='Ver boton comienzo', compute='_compute_view_button_start', store=True)
	view_button_stop = fields.Boolean(string='Ver boton comienzo', compute='_compute_view_button_start', store=True)

	def _compute_view_button_start(self):
		self.ensure_one()
		if self.env.user:
			employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('company_id', '=', self.env.company.id)])
			if employee:
				now = fields.Datetime.now()
				attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_in', '<=', now), ('check_out', '=', False)], order="check_in desc", limit=1)
				if attendance:
					aal = self.env['account.analytic.line'].search([('attendance_id', '=', attendance.id), ('employee_id', '=', employee.id)])
					if aal:
						return False
					else:
						return True
				else:
					return False
			else:
				return False
		else:
			return False
		
	def _compute_view_button_start(self):
		self.ensure_one()
		if self.env.user:
			employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('company_id', '=', self.env.company.id)])
			if employee:
				now = fields.Datetime.now()
				attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_in', '<=', now), ('check_out', '=', False)], order="check_in desc", limit=1)
				if attendance:
					aal = self.env['account.analytic.line'].search([('attendance_id', '=', attendance.id), ('employee_id', '=', employee.id), ('task_id', '=', self.id)])
					if aal:
						return True
					else:
						return False
				else:
					return False
			else:
				return False
		else:
			return False

	""" def get_start_geolocation(self):
		self.ensure_one()
		if self.env.user:
			employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('company_id', '=', self.env.company.id)])
			if employee:
				now = fields.Datetime.now()
				attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_in', '<=', now), ('check_out', '=', False)], order="check_in desc", limit=1)
				if attendance:
					return self.button_start_work()
				else:
					raise exceptions.UserError(_(
					'El usuario %(user_name)s, no ha iniciado la geolocalización. Debe iniciarla desde el botón rojo a la izquiera de su nombre.',
					user_name=self.env.user.name))
			else:
				raise exceptions.UserError(_(
					'El usuario %(user_name)s, no tiene empleado asociado para la actual compañia.',
					user_name=self.env.user.name))

	def get_stop_geolocation(self):
		self.ensure_one()
		if self.env.user:
			employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('company_id', '=', self.env.company.id)])
			if employee:
				now = fields.Datetime.now()
				attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_in', '<=', now), ('check_out', '=', False)], order="check_in desc", limit=1)
				if attendance in self.timesheet_ids.mapped('attendance_id'):
					return self.button_end_work()
				else:
					raise exceptions.UserError(_(
					'El usuario %(user_name)s, la geolocalización no esta iniciada o esta iniciada para otra tarea.',
					user_name=self.env.user.name))
			else:
				raise exceptions.UserError(_(
					'El usuario %(user_name)s, no tiene empleado asociado para la actual compañia.',
					user_name=self.env.user.name))
		
 """