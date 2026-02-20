# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self, group_id=False):
        """
        Inyectamos la descripción de la línea de venta en los valores de abastecimiento.
        """
        values = super()._prepare_procurement_values(group_id=group_id)
        
        if self.name:
            values['sale_line_custom_description'] = self.name
            
        return values