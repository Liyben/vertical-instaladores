# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    include_in_mail_composer = fields.Boolean(
        string="Incluir en correos",
        help="Si está marcado, este contacto se añadirá automáticamente como destinatario al enviar presupuestos o facturas del contacto principal.",
        default=False
    )