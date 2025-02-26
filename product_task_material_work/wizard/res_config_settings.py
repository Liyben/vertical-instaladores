# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    active_group_percent_waste = fields.Boolean(
        string="Desperdicio",
        help="Añade un porcentaje de desperdicio al producto partida para obtener el coste total.",
        implied_group='product_task_material_work.group_percent_waste',
        config_parameter='product_task_material_work.active_group_percent_waste',
    )