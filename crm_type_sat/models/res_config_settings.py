# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stage_sat_id = fields.Many2one('crm.stage', string='Etapa para SAT', domain="[('is_won', '=', True), ('type', 'in', ['sat', 'both'])]", config_parameter='crm_type_sat.default_stage_sat')

    stage_opportunity_id = fields.Many2one(domain="[('is_won', '=', True), ('type', 'in', ['opportunity', 'both'])]")