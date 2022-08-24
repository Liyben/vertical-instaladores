# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import string
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    
    supplier_pick_number = fields.Char(string='Nº. albarán proveedor')
    use_supplier_pick_number = fields.Boolean(related='picking_type_id.use_supplier_pick_number',
        readonly=True)

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    use_supplier_pick_number = fields.Boolean(string='Tiene número de albarán')