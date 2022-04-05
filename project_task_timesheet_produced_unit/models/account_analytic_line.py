# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _


class AccountAnalyticLine(models.Model):
	_inherit = "account.analytic.line"

	produced_unit = fields.Float(
		"Unidades producidas",
		digits='Product Unit of Measure',
	)
	