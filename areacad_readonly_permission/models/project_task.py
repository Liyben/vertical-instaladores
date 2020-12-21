# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime
from odoo import fields, models, api, _, exceptions

class ProjectTaskTimeSheet(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    @api.onchange('date_end','date_start','unit_amount')
    def _onchange_date_end_start(self):
        for time_line in self:
            if time_line.date_start and time_line.date_end:
                if time_line.date_start <= time_line.date_end:
                    diff = fields.Datetime.from_string(time_line.date_end) - fields.Datetime.from_string(time_line.date_start)
                    time_line.timer_duration = round(diff.total_seconds() / 60.0, 2)
                    time_line.unit_amount = round(diff.total_seconds() / (60.0 * 60.0), 2)
                else: 
                    raise exceptions.ValidationError('La fecha de inicio debe ser menor que la fecha fin.')
            else:
                time_line.unit_amount = 0.0
                time_line.timer_duration = 0.0

