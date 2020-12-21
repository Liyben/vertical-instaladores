# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class SaleOrder(models.Model):

	_inherit='sale.order'

	#Obtiene el valor por defecto de linea de negocio
	def _get_default_parent_analytic_account_id(self):
		if self._context.get('parent_analytic_account_id') or self._context.get('default_parent_analytic_account_id'):
			return self._context.get('parent_analytic_account_id') or self._context.get('default_parent_analytic_account_id')

		parent_analytic_account = self.env.ref('sale_order_parent_analytic_account.analytic_my_company', raise_if_not_found=False)
		if parent_analytic_account:
			return parent_analytic_account.id

	#Campo cuenta analitica madre
	parent_analytic_account_id = fields.Many2one('account.analytic.account', 'Línea Negocio', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Cuenta analítica madre relacionada con el pedido de venta.", copy=False, default=_get_default_parent_analytic_account_id)

	#Dominio dinamico de la cuenta analítica madre para la cuenta analitica
	@api.onchange('parent_analytic_account_id','partner_id')
	def _onchange_parent_analytic_account_id(self):
		domain = {}
		analytic_account_list = []

		

		if self.parent_analytic_account_id:
			#buscamos las cuentas analiticas que tienen como madre la linea de negocio
			analytic_account_obj = self.env['account.analytic.account'].search(['|',('id', '=', self.parent_analytic_account_id.id) ,'&', ('parent_id','=',self.parent_analytic_account_id.id), ('partner_id','=',self.partner_id.id)])
			for analytic_account_ids in analytic_account_obj:
				analytic_account_list.append(analytic_account_ids.id)
			#asignamos la lista de cuenta analiticas al dominio
			domain = {'analytic_account_id': [('id', 'in', analytic_account_list)]}

		return { 'domain' : domain}

	#Redefiminimos el método donde se crea la cuenta analitica para que tenga en cuenta la cuenta analitica madre
	@api.multi
	def _create_analytic_account(self, prefix=None):
		for order in self:
			name = order.name
			if prefix:
				name = prefix + ": " + order.name
			analytic = self.env['account.analytic.account'].create({
				'name': name,
				'code': order.client_order_ref,
				'company_id': order.company_id.id,
				'partner_id': order.partner_id.id,
				'parent_id': order.parent_analytic_account_id.id
				}) 
			order.analytic_account_id = analytic
	