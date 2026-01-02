# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    
    _inherit='sale.order'

    #Cuenta analítica madre
    analytic_account_parent_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Cuenta analítica madre",
        copy=False, check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    @api.onchange('team_id')
    def _onchange_team_id_to_analytic_account_parent_id(self):
        for record in self:
            if record.team_id and record.team_id.analytic_account_parent_id:
                record.analytic_account_parent_id = record.team_id.analytic_account_parent_id.id
            else:
                record.analytic_account_parent_id = False
                
    #Override función para los datos de la cuenta analitica
    def _prepare_analytic_account_data(self, prefix=None):
        """ Prepare SO analytic account creation values.

        :param str prefix: The prefix of the to-be-created analytic account name
        :return: `account.analytic.account` creation values
        :rtype: dict
        """
        self.ensure_one()
        name = self.name
        if prefix:
            name = prefix + ": " + self.name
        plan = self.plan_id
        if not plan:
            plan = self.env['account.analytic.plan'].sudo().search([], limit=1)
        
        analytic_account_parent = self.analytic_account_parent_id

        return {
            'name': name,
            'code': self.client_order_ref,
            'company_id': self.company_id.id,
            'plan_id': plan.id or False,
            'partner_id': self.partner_id.id,
            'parent_id': analytic_account_parent.id or False,
        }
