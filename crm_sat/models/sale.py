# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        if self.opportunity_id and self.opportunity_id.type == 'opportunity':
            stage_id = int(self.env['ir.config_parameter'].sudo().get_param('crm_sat.default_stage_opportunity'))
            if stage_id:
                self.opportunity_id.stage_id = stage_id
        return res
     
    def _compute_partner_shipping_id(self):
        super()._compute_partner_shipping_id()
        for sale in self:
            if sale.opportunity_id and sale.opportunity_id.partner_id.id == sale.partner_id.id:
                if sale.opportunity_id.partner_shipping_id:
                    sale.partner_shipping_id = sale.opportunity_id.partner_shipping_id.id