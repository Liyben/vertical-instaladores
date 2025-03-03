# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class ResPartner(models.Model):
    
    _inherit = "res.partner"
    
    def _get_next_ref(self, vals=None):
        if vals.get('customer_rank') and not vals.get('supplier_rank'):
            return self.env['ir.sequence'].next_by_code('res.partner.customer')
        elif vals.get('supplier_rank') and not vals.get('customer_rank'):
            return self.env['ir.sequence'].next_by_code('res.partner.supplier')
        else:  
            return self.env["ir.sequence"].next_by_code("res.partner")