# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    #Cuenta analítica madre
    analytic_account_parent_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Cuenta analítica madre",
        copy=False, check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")