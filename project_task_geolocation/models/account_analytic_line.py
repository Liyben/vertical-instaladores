# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import re
from odoo import api, fields, models, exceptions, _


class AccountAnalyticLine(models.Model):
	_inherit = "account.analytic.line"

	attendance_id = fields.Many2one('hr.attendance', store=True, readonly=True)
	view_button_stop = fields.Boolean(related='task_id.view_button_stop' )

