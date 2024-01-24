# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_use_product_name_and_description_per_so_line = fields.Boolean(
        string="Usar el nombre y la descripción de venta del producto en la descripción de la línea de pedido.",
        implied_group="sale_order_line_description.group_use_product_name_and_description_per_so_line",
    )
