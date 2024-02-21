# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stage_opportunity_id = fields.Many2one('crm.stage', string='Etapa para oportunidad', domain="[('is_won', '=', True)]", config_parameter='lyb_crm_sat.default_stage_opportunity')

