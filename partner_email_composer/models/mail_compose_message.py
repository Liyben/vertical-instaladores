# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.depends('composition_mode', 'model', 'parent_id', 'res_domain', 'res_ids', 'template_id')
    def _compute_partner_ids(self):
        # 1. Dejamos que Odoo calcule los destinatarios nativos (plantilla, parent_id, etc.)
        super()._compute_partner_ids()
        
        # 2. Interceptamos para añadir nuestros contactos personalizados
        for composer in self:
            if composer.model in ['sale.order', 'account.move', 'purchase.order']:  # Ajustado según los modelos relevantes
                # Usamos el método nativo expuesto en tu código para evaluar IDs de forma segura
                res_ids = composer._evaluate_res_ids()
                
                if not res_ids:
                    continue
                    
                records = self.env[composer.model].browse(res_ids)
                
                # Usamos mapped() para recolectar todos los hijos de todos los registros activos
                # y filtramos por nuestro campo personalizado
                extra_partners = records.mapped('partner_id.child_ids').filtered('include_in_mail_composer')
                
                if extra_partners:
                    # El operador |= une los recordsets sin duplicados, preservando el cliente principal
                    composer.partner_ids |= extra_partners