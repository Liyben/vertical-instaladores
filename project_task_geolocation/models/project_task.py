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
		if (location):
			self.write({'latitude': location[0], 'longitude': location[1]})

	def button_start_work(self):
		result = super().button_start_work()
		result["context"].update({
			"default_start_latitude": self.latitude,
			"default_start_longitude": self.longitude,
		})
		return result

