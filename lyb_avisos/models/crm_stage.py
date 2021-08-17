# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class Stage(models.Model):
	_inherit = 'crm.stage'

	crm_sub_type = fields.Selection(
		[('notice', 'Aviso'), ('opportunity', 'Oportunidad'), ('both', 'Ambos')],
		string='Subtipo', required=True, default='both',
		help="Este campo es usado para distinguir las etapas de Avisos"
			 "de las etapas relacionadas a las Oportunidades, o especificar"
			 "etapas disponibles para ambos.")