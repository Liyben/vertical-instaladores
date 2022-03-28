# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class Stage(models.Model):
	_inherit = 'crm.stage'
	@api.model
	def _get_activity_type_id_domain(self):

		crm_id = self.env.ref('crm.model_crm_stage').id
		return ['|', ('res_model_id', '=', False), ('res_model_id', '=', crm_id)]

	activity_type_id = fields.Many2one(
		'mail.activity.type', string='Tipo de actividad',
		domain=_get_activity_type_id_domain, ondelete='restrict')