# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class Stage(models.Model):
	_inherit = 'crm.stage'

	activity_type_id = fields.Many2one(
		'mail.activity.type', string='Tipo de actividad',
		domain="['|', ('res_model_id', '=', False), ('res_model_id', '=', ref('crm.model_crm_stage'))]", ondelete='restrict')