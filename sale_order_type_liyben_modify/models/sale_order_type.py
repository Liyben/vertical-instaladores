# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class SaleOrderTypology(models.Model):
	_inherit = 'sale.order.type'

	default_debit_account_id = fields.Many2one('account.account', string='Cuenta deudora por defecto', domain=[('deprecated', '=', False)], 
		help="Actúa como una cuenta por defecto para importes en el debe")

	account_id = fields.Many2one('account.account', string='Cuenta a cobrar por defecto',
		domain=[('deprecated', '=', False)], help="La cuenta que será usada para la factura")
	
	tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
	