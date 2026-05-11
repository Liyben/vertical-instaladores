# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_product_multiline_description_sale(self):
        """
        Sobrescribimos el método nativo para cambiar la regla de generación
        del nombre base en ventas, omitiendo la referencia interna.
        
        1. Si tiene descripción de venta, usar SOLO la descripción.
        2. Si no tiene, usar el nombre del producto.
        """
        self.ensure_one()
        
        # El contexto (idioma) ya viene inyectado desde la llamada en sale_order_line
        # Si tiene descripción de venta, usar SOLO la descripción.
        if self.description_sale:
            return self.description_sale
        
        # Si no tiene, usar EXCLUSIVAMENTE el nombre del producto.
        return self.name