# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class AccountAnalyticAccount(models.Model):

	_inherit='account.analytic.account'

	#Campo tipo de cuenta analitica
	type_analytic_account = fields.Selection([('activity','Lineas de negocio')],string='Tipo')
	
	#Cliente vacio al elegir 'Linea de negocio'
	@api.onchange('type_analytic_account')
	def _onchange_type_analytic_account(self):
		for aa in self:
			if aa.type_analytic_account == 'activity':
				aa.partner_id = False