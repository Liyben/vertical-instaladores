# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('product_id', 'move_id.payment_reference')
    def _compute_name(self):
        # 1. Ejecutamos la lógica nativa primero. Esto procesa el texto estándar de Odoo 
        # y gestiona las lógicas complejas del core (como los payment_terms).
        super()._compute_name()

        # 2. Filtramos para afectar solo a las líneas editables y que sean productos reales.
        for line in self.filtered(lambda l: l.move_id.inalterable_hash is False and l.display_type not in ('line_section', 'line_note')):
            
            # Solo aplicamos en facturas de cliente (ventas)
            if line.journal_id.type == 'sale':
                
                # Si el producto está vacío, el valor de name será vacío.
                if not line.product_id:
                    # Lo forzamos a vacío solo si el core no lo limpió ya
                    if line.name:
                        line.name = False
                    continue

                # Contexto de traducción del producto basado en el idioma del cliente
                lang = line.move_id.partner_id.lang or line.partner_id.lang
                product = line.product_id.with_context(lang=lang) if lang else line.product_id
                
                # --- A. Recrear el nombre nativo para la validación ---
                standard_values = []
                if product.partner_ref:
                    standard_values.append(product.partner_ref)
                if product.description_sale:
                    standard_values.append(product.description_sale)
                expected_base_name = '\n'.join(standard_values) if standard_values else False

                # --- B. Aplicar: ---
                # 1. Si tiene descripción de venta, usarla.
                # 2. Si no, usar el nombre del producto.
                custom_name = product.description_sale or product.name

                # --- C. Validación de Seguridad ---
                # Verificamos si el nombre en la vista es el que Odoo puso por defecto,
                # si está vacío, o si ya tiene nuestra regla aplicada. 
                if not line.name or line.name == expected_base_name or line.name == custom_name:
                    line.name = custom_name