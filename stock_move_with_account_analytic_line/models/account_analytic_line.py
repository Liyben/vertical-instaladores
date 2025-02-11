# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    stock_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Movimiento de stock",
    )