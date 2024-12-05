# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class Stage(models.Model):
	_inherit = 'crm.stage'

	type = fields.Selection(
		[('sat', 'SAT'), ('opportunity', 'Oportunidad'), ('both', 'Ambos')],
		string='Tipo', required=True, default='both',
		help="Este campo es usado para distinguir las etapas de SAT"
			 "de las etapas relacionadas a las Oportunidades, o especificar"
			 "etapas disponibles para ambos.")