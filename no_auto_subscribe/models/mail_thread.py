# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).from . import data
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class MailThread(models.Model):
    _inherit = 'mail.thread'

    def _message_auto_subscribe(self, updated_values, followers_existing_policy='skip'):
        """
        Sobrescribe la lógica base de Odoo 17 para anular la autosuscripción.
        Normalmente, Odoo retorna un diccionario de {partner_id: [subtype_ids]} 
        indicando quién debe seguir el registro y qué subtipos escucha.
        
        Al retornar un diccionario vacío {}, garantizamos que el registro nazca
        y se modifique sin añadir ningún seguidor automático a nivel de ORM.
        Solo se añadirán si un usuario hace clic explícitamente en "Seguir".
        """
        return {}