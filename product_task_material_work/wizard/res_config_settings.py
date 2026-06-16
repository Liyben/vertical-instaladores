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

    """ active_group_sales_apply_pricelist = fields.Boolean(
        string="Tarifa en Productos Partida",
        help="Permite aplicar la tarifa en las líneas de materiales y mano de obra en lugar del producto partida",
        implied_group='product_task_material_work.group_sales_apply_pricelist',
        config_parameter='product_task_material_work.active_group_sales_apply_pricelist',
    ) """

    print_works_hours_on_detailed_time = fields.Boolean(
        related='company_id.print_works_hours_on_detailed_time',
        readonly=False,
    )
    
    print_materials_qty_on_detailed_materials = fields.Boolean(
        related='company_id.print_materials_qty_on_detailed_materials',
        readonly=False,
    )