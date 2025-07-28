# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('amount_untaxed', 'amount_total', 'percent_retention')
    def _amount_all_retention(self):
        for order in self:
            order.amount_retention = order.amount_untaxed * order.percent_retention / 100
            order.amount_to_pay = order.amount_total - order.amount_retention

    percent_retention = fields.Float(
        string="Retención (%)",
        digits="Retention",
        readonly=False,
    )

    amount_retention = fields.Monetary(
        string="Retención", 
        store=True, 
        readonly=True,
        compute='_amount_all_retention', 
    )

    amount_to_pay = fields.Monetary(
        string="Total a pagar", 
        store=True, 
        readonly=True,
        compute='_amount_all_retention', 
    )