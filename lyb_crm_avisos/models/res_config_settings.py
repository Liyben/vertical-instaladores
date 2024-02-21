# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stage_notice_id = fields.Many2one('crm.stage', string='Etapa para aviso', domain="[('is_won', '=', True), ('crm_sub_type', 'in', ['notice', 'both'])]", config_parameter='lyb_crm_sat.default_stage_notice')

    stage_opportunity_id = fields.Many2one(domain="[('is_won', '=', True), ('crm_sub_type', 'in', ['opportunity', 'both'])]")