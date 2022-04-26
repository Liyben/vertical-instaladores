# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _


class HrTimesheetSwitch(models.TransientModel):
	_inherit = "hr.timesheet.switch"


	@api.model
	def default_get(self, fields_list):
		result = super().default_get(fields_list)
		
		result['start_latitude'] = result['task_id'].latitude
		result['start_longitude'] = result['task_id'].longitude
		result['end_latitude'] = 0.0
		result['end_longitude'] = 0.0
		return result