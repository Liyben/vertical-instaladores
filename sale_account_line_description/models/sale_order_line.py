# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id')
    def _compute_name(self):
        # --- REGLA 1 ---
        # Intervenimos antes de que el core evalúe el compute.
        # Si el usuario borra el producto, borramos la descripción.
        for line in self:
            if not line.product_id and not line.display_type:
                line.name = False
        
        # Ejecutamos el comportamiento estándar.
        # Este método llamará nativamente a get_product_multiline_description_sale()
        # el cual ya hemos sobrescrito en product.product.
        super()._compute_name()