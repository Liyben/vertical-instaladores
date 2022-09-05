# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    aviso_ids = fields.One2many('crm.lead', 'partner_id', string='Avisos', domain=[('type','=','opportunity'),('sub_type','=','notice')])
    aviso_count = fields.Integer("Aviso", compute='_compute_aviso_count')

    def _compute_aviso_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        opportunity_data = self.env['crm.lead'].read_group(
            domain=[('partner_id', 'in', all_partners.ids),('type', '=', 'opportunity'),('sub_type','=','notice')],
            fields=['partner_id'], groupby=['partner_id']
        )

        self.aviso_count = 0
        for group in opportunity_data:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.aviso_count += group['partner_id_count']
                partner = partner.parent_id

    def action_view_notice(self):
        '''
        This function returns an action that displays the notices from partner.
        '''
        action = self.env['ir.actions.act_window']._for_xml_id('lyb_crm_avisos.lyb_avisos_action_your_avisos')
        if self.is_company:
            action['domain'] = [('partner_id.commercial_partner_id.id', '=', self.id),('type', '=', 'opportunity'),('sub_type','=','notice')]
        else:
            action['domain'] = [('partner_id.id', '=', self.id),('type', '=', 'opportunity'),('sub_type','=','notice')]
        return action