# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        if self.opportunity_id and self.opportunity_id.sub_type == 'notice':
            stage_id = int(self.env['ir.config_parameter'].sudo().get_param('lyb_crm_avisos.default_stage_notice'))
            if stage_id:
                self.opportunity_id.stage_id = stage_id
        return res