# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    
    _inherit='sale.order'

    #Campo para el plan analitico
    plan_id = fields.Many2one(
        'account.analytic.plan',
        string='Plan analítico',
    )

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        for record in self:
            if record.analytic_account_id.plan_id:
                record.plan_id = record.analytic_account_id.plan_id.id

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
            #plan = self.env['account.analytic.plan'].sudo().search([], limit=1)
            plan = self.env['account.analytic.plan'].sudo().create({
                'name': name,
            })
        return {
            'name': name,
            'code': self.client_order_ref,
            'company_id': self.company_id.id,
            'plan_id': plan.id,
            'partner_id': self.partner_id.id,
        }
