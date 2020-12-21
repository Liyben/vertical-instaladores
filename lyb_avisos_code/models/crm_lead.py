# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    sequence_code = fields.Char(
        string='Nº serie', default="/", readonly=True)

    @api.model
    def create(self, vals):
        result = super(CrmLead, self).create(vals)
        if (result.sub_type == 'notice'):
            result.sequence_code = self.env['ir.sequence'].next_by_code('notice.code')
        elif (result.sub_type == 'opportunity'):
            result.sequence_code = self.env['ir.sequence'].next_by_code('opportunity.code')
    
        return result
