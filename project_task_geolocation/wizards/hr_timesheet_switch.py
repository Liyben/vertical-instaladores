# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _


class HrTimesheetSwitch(models.TransientModel):
	_inherit = "hr.timesheet.switch"


	@api.model
	def default_get(self, fields_list):
		"""Return defaults depending on the context where it is called."""
		result = super().default_get(fields_list)
		inherited = self._closest_suggestion()
		assert inherited._name == "account.analytic.line"
		# Inherit all possible fields from that account.analytic.line record
		if inherited:
			# Convert inherited to RPC-style values
			_fields = set(fields_list) & set(inherited._fields) - {
				# These fields must always be reset
				"id",
				"amount",
				"date_time",
				"date_time_end",
				"date",
				"is_task_closed",
				"unit_amount",
				# This field is from sale_timesheet, which is not among
				# this module dependencies; ignoring it will let you
				# resume an invoiced AAL if that module is installed,
				# and it doesn't hurt here
				"timesheet_invoice_id",
				# These fields are from the hr_timesheet_activity_begin_end
				# module. Unless ignored, these fields will cause a validation
				# error because time_stop - time_start must equal duration.
				"time_start",
				"time_stop",
				"name",
				"start_latitude",
				"start_longitude",
				"end_latitude",
				"end_longitude",
			}
			inherited.read(_fields)
			values = inherited._convert_to_write(inherited._cache)
			for field in _fields:
				result[field] = values[field]
		return result