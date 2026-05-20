# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_send_and_print(self):
        """ Intercepta el nuevo wizard de Odoo 17 para facturas """
        action = super().action_send_and_print()
        
        # Operamos solo si es un único registro
        if len(self) == 1 and self.partner_id:
            extra_partners = self.partner_id.child_ids.filtered('include_in_mail_composer')
            
            if extra_partners:
                ctx = action.get('context', {})
                
                # Unimos el contacto principal con los hijos para no perderlo
                all_partners = self.partner_id | extra_partners
                
                # El wizard account.move.send usa default_mail_partner_ids
                ctx['default_mail_partner_ids'] = all_partners.ids
                action['context'] = ctx
                
        return action