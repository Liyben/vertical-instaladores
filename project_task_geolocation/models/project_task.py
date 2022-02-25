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
			self.latitude = location[0]
			self.longitude = location[1]
		elif (location[0] == 0.0):
			_logger.debug("PASA CERO LOCATION")
		else:
			_logger.debug("NO PASA DATOS LOCATION")

