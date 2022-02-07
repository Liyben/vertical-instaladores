# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class AccountMove(models.Model):
	_inherit = "account.move"


	@api.depends('invoice_line_ids.price_subtotal', 'amount_tax', 'currency_id', 'company_id', 'invoice_date', 'move_type', 'percent_retention')
	def _amount_all_retention(self):
		for invoice in self:
			invoice.amount_retention = invoice.amount_untaxed * invoice.percent_retention / 100
			invoice.amount_to_pay = invoice.amount_total - invoice.amount_retention

	
	percent_retention = fields.Float(string='Retención (%)', digits='Discount', default=0.0, readonly=True,
									  states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	amount_retention = fields.Monetary(string='Retención', store=True, readonly=True, compute='_amount_all_retention')
	amount_to_pay = fields.Monetary(string='Total a pagar', store=True, readonly=True, compute='_amount_all_retention')
	
