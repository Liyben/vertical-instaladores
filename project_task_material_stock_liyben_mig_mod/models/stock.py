# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import string
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    stock_move_from_task = fields.Boolean(string='Tipo de albaran para la tarea.')