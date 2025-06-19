# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    create_date_order = fields.Datetime(
        string="Fecha de creación",
        required=False, copy=False,
        help="Fecha de creación del pedido de venta.",
        default=fields.Datetime.now)
    