# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values):
        """
        Capturamos la descripción de la línea de venta inyectada en el procurement
        y la asignamos al movimiento de stock.
        """
        move_values = super()._get_stock_move_values(
            product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values
        )
        
        if values.get('sale_line_custom_description'):
            # Asignamos la descripción al nombre principal del movimiento
            move_values['name'] = values.get('sale_line_custom_description')
            
            # Opcional: Si además se quiere que sobrescriba el campo 'description_picking'
            # move_values['description_picking'] = values.get('sale_line_custom_description')
            
        return move_values