# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
	_inherit = 'crm.lead'

	#Obtiene el valor por defecto de linea de negocio
	def _get_default_parent_analytic_account_id(self):
		if self._context.get('parent_analytic_account_id') or self._context.get('default_parent_analytic_account_id'):
			return self._context.get('parent_analytic_account_id') or self._context.get('default_parent_analytic_account_id')

		parent_analytic_account = self.env.ref('sale_order_parent_analytic_account.analytic_my_company', raise_if_not_found=False)
		if parent_analytic_account:
			return parent_analytic_account.id

    #Campo cuenta analitica madre relacionada con el proyecto
	parent_analytic_account_id = fields.Many2one('account.analytic.account', string='Línea Negocio', domain=[('type_analytic_account', '=', 'activity')], default=_get_default_parent_analytic_account_id)

	#Cuenta analitica del proyecto asociado
	analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica', store=True, related='project_id.analytic_account_id')

	#Dominio dinamico de la cuenta analítica madre para el proyecto
	@api.onchange('parent_analytic_account_id','partner_id')
	def _onchange_parent_analytic_account_id(self):
		domain = {}
		analytic_account_list = []
		self.project_id = False
		if self.parent_analytic_account_id:
			#buscamos las cuentas analiticas que tienen como madre la linea de negocio
			analytic_account_obj = self.env['account.analytic.account'].search(['|',('id', '=', self.parent_analytic_account_id.id) ,'&', ('parent_id','=',self.parent_analytic_account_id.id), ('partner_id','=',self.partner_id.id)])
			for analytic_account_ids in analytic_account_obj:
				analytic_account_list.append(analytic_account_ids.id)
			#asignamos la lista de cuenta analiticas al dominio
			domain = {'project_id': [('analytic_account_id', 'in', analytic_account_list)]}

		return { 'domain' : domain}
