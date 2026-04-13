# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Sobrescribimos el campo únicamente para actualizar el dominio
    opportunity_id = fields.Many2one(
        domain="[('type', 'in', ('opportunity', 'sat')), '|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )