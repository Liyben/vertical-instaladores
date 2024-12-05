# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.osv import expression

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sat_ids = fields.One2many('crm.lead', 'partner_id', string='SAT', domain=[('type','=','sat')])
    sat_count = fields.Integer("Aviso", compute='_compute_sat_count')

    def _compute_sat_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search_fetch(
            [('id', 'child_of', self.ids)], ['parent_id'],
        )

        sat_data = self.env['crm.lead'].with_context(active_test=False)._read_group(
            domain=[('partner_id', 'in', all_partners.ids),('type', '=', 'sat')],
            groupby=['partner_id'], aggregates=['__count']
        )
        self_ids = set(self._ids)

        self.sat_count = 0
        for partner, count in sat_data:
            while partner:
                if partner.id in self_ids:
                    partner.sat_count += count
                partner = partner.parent_id

    def action_view_sat(self):
        '''
        This function returns an action that displays the sat from partner.
        '''
        action = self.env['ir.actions.act_window']._for_xml_id('crm_type_sat.action_your_sat')
        action['context'] = {}
        if self.is_company:
            action['domain'] = [('partner_id.commercial_partner_id', '=', self.id)]
        else:
            action['domain'] = [('partner_id', '=', self.id)]
        action['domain'] = expression.AND([action['domain'], [('active', 'in', [True, False])]])
        action['domain'] = expression.AND([action['domain'], [('type', '=', 'sat')]])
        return action