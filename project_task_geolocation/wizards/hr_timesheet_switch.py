# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
import logging
_logger = logging.getLogger(__name__)

class HrTimesheetSwitch(models.TransientModel):
	_inherit = "hr.timesheet.switch"


	""" @api.model
	def default_get(self, fields_list):
		result = super().default_get(fields_list)
		if 'task_id' in result:
			result['start_latitude'] = self.env["project.task"].search([("id", "=", result['task_id'])]).latitude
			result['start_longitude'] = self.env["project.task"].search([("id", "=", result['task_id'])]).longitude
			result['end_latitude'] = 0.0
			result['end_longitude'] = 0.0
		return result """

	def action_switch(self):
		"""Stop old timer, start new one."""
		self.ensure_one()
		# Stop old timer
		self.with_context(
			resuming_lines=self.ids,
			stop_dt=self.date_time,
		).running_timer_id.button_end_work()
		# Start new timer
		_fields = self.env["account.analytic.line"]._fields.keys()
		self.read(_fields)
		values = self._convert_to_write(self._cache)
		new = self.env["account.analytic.line"].create(
			{field: value for (field, value) in values.items() if field in _fields}
		)
		# Change latitude and longitude
		for rec in new:
			rec.start_latitude = rec.task_id.latitude
			rec.start_longitude = rec.task_id.longitude
			rec.end_latitude = 0.0
			rec.end_longitude = 0.0
		# Display created timer record if requested
		if self.env.context.get("show_created_timer"):
			form_view = self.env.ref("hr_timesheet.hr_timesheet_line_form")
			return {
				"res_id": new.id,
				"res_model": new._name,
				"type": "ir.actions.act_window",
				"view_mode": "form",
				"view_type": "form",
				"views": [(form_view.id, "form")],
			}
		# Close wizard and reload view
		return {
			"type": "ir.actions.act_multi",
			"actions": [
				{"type": "ir.actions.act_window_close"},
				{"type": "ir.actions.act_view_reload"},
			],
		}