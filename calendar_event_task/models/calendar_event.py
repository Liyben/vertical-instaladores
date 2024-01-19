# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _

class CalendarEvent(models.Model):
	_inherit = "calendar.event"

	task_id = fields.Many2one('project.task', 'Tarea', index=True)