# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    print_works_hours_on_detailed_time = fields.Boolean(
        string="Imprimir Horas con Tiempo Detallado",
        default=True,
        help="Si está marcado, las horas se imprimen si hay tiempo detallado. Si se desmarca, se evalúa el precio del tiempo detallado."
    )
    
    print_materials_qty_on_detailed_materials = fields.Boolean(
        string="Imprimir Cantidades con Materiales Detallados",
        default=True,
        help="Si está marcado, las cantidades se imprimen si hay materiales detallados. Si se desmarca, se evalúa el precio del material."
    )