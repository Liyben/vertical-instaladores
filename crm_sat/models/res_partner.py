# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.osv import expression

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _compute_opportunity_count(self):
        super()._compute_opportunity_count()
        all_partners = self.with_context(active_test=False).search_fetch(
            [('id', 'child_of', self.ids)], ['parent_id'],
        )

        opportunity_data = self.env['crm.lead'].with_context(active_test=False)._read_group(
            domain=[('partner_id', 'in', all_partners.ids),('type', '=', 'opportunity')],
            groupby=['partner_id'], aggregates=['__count']
        )
        self_ids = set(self._ids)

        self.opportunity_count = 0
        for partner, count in opportunity_data:
            while partner:
                if partner.id in self_ids:
                    partner.opportunity_count += count
                partner = partner.parent_id

    def action_view_opportunity(self):
        '''
        This function returns an action that displays the opportunities from partner.
        '''
        action = super().action_view_opportunity()
        action['domain'] = expression.AND([action['domain'], [('type', '=', 'opportunity')]])
        return action
