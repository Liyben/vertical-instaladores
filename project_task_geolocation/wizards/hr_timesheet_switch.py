# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
import logging
_logger = logging.getLogger(__name__)

class HrTimesheetSwitch(models.TransientModel):
    _inherit = "hr.timesheet.switch"

    def action_switch(self):
        """Stop old timer, start new one."""
        self.ensure_one()
        # Stop old timer
        self.with_context(
            resuming_lines=self.ids,
            stop_dt=self.date_time,
        ).running_timer_id.button_end_work()
        # Start new timer
        if self.analytic_line_id:
            new = self.analytic_line_id.copy(self._prepare_copy_values(self))
        else:
            fields = self.env["account.analytic.line"]._fields.keys()
            vals = self.env["account.analytic.line"].default_get(fields)
            vals.update(self._prepare_copy_values(self))
            if self.env.user.has_group('project_task_geolocation.group_geolocation_worker'):
                employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('company_id', '=', self.env.company.id)])
                if employee:
                    now = fields.Datetime.now()
                    attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_in', '<=', now), ('check_out', '=', False)], order="check_in desc", limit=1)
                    aal = self.env['account.analytic.line'].search([('attendance_id', '=', attendance.id), ('employee_id', '=', employee.id)])
                    if attendance and not aal:
                        vals.update({
                        "attendance_id": attendance.id,
                        })
            new = self.env["account.analytic.line"].create(vals)
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