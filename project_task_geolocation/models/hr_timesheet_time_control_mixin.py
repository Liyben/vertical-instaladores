# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class HrTimesheetTimeControlMixin(models.AbstractModel):
	_inherit = "hr.timesheet.time_control.mixin"


	show_geolocation_control = fields.Selection(
		selection=[("check-in", "Check-In"), ("start", "Start"), ("check-out", "Check-Out"), ("stop", "Stop")],
		help="Indica que boton de control mostrar.",
	)

	def get_check_in_geolocation(self):
		for record in self:
			record.show_geolocation_control = 'start'

	def get_start_geolocation(self):
		for record in self:
			record.show_geolocation_control = 'check-out'

	def get_check_out_geolocation(self):
		for record in self:
			record.show_geolocation_control = 'stop'

	def get_stop_geolocation(self):
		for record in self:
			record.show_geolocation_control = 'check-in'