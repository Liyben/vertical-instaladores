# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class ResCompany(models.Model):
	_inherit = 'res.company'

	maximum_hours_per_day = fields.Float(
		string='Maximas horas por dia',
		digits=(2, 2), default=8.0)
