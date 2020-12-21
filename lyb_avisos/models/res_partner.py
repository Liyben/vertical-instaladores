# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    aviso_ids = fields.One2many('crm.lead', 'partner_id', string='Avisos', domain=[('type','=','opportunity'),('sub_type','=','notice')])
    opportunity_ids = fields.One2many('crm.lead', 'partner_id', string='Opportunities', domain=[('type', '=', 'opportunity'),('sub_type','=','opportunity')])
    aviso_count = fields.Integer("Aviso", compute='_compute_aviso_count')

    @api.multi
    def _compute_aviso_count(self):
        for partner in self:
            operator = 'child_of' if partner.is_company else '='  
            partner.aviso_count = self.env['crm.lead'].search_count([('partner_id', operator, partner.id), ('type', '=', 'opportunity'),('sub_type','=','notice')])

    @api.multi
    def _compute_opportunity_count(self):
        for partner in self:
            operator = 'child_of' if partner.is_company else '='
            partner.opportunity_count = self.env['crm.lead'].search_count([('partner_id', operator, partner.id), ('type', '=', 'opportunity'),('sub_type','=','opportunity')])