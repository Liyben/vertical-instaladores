# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
import logging
_logger = logging.getLogger(__name__)

class HrTimesheetSwitch(models.TransientModel):
	_inherit = "hr.timesheet.switch"


	@api.model
	def default_get(self, fields_list):
		result = super().default_get(fields_list)
		_logger.debug('ID TASK %d', result['task_id'])
		result['start_latitude'] = self.env["project.task"].search([("id", "=", result['task_id'])]).latitude
		result['start_longitude'] = self.env["project.task"].search([("id", "=", result['task_id'])]).longitude
		result['end_latitude'] = 0.0
		result['end_longitude'] = 0.0
		return result