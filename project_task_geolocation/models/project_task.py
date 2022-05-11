# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
	_inherit = 'project.task'

	latitude = fields.Float(
		"Latitude",
		digits='Geolocalización',
		readonly=True
	)
	longitude = fields.Float(
		"Longitude",
		digits='Geolocalización',
		readonly=True
	)

	def get_current_geolocation(self, location=False):
		for record in self:
			if (location):
				record.write({'latitude': location[0], 'longitude': location[1]})

	def get_start_geolocation(self):
		super().get_start_geolocation()
		result = self.button_start_work()
		result["context"].update({
			"default_start_latitude": self.latitude,
			"default_start_longitude": self.longitude,
		})
		return result

	def get_stop_geolocation(self):
		super().get_stop_geolocation()
		self.button_end_work()

	@api.depends(
		"project_id.allow_timesheets",
		"timesheet_ids.employee_id",
		"timesheet_ids.unit_amount",
	)
	def _compute_show_time_control(self):
		result = super()._compute_show_time_control()
		for task in self:
			if task.show_time_control == 'start' and task.show_geolocation_control == 'check-out':
				task.show_geolocation_control = 'start'
			""" if not task.timesheet_ids:
				task.show_geolocation_control = 'check-in' """
		return result
