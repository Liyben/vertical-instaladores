# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv
from openerp import api, models, fields
import openerp.addons.decimal_precision as dp


class AccountInvoice(models.Model):
	_inherit = "account.invoice"


	@api.one
	@api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
				 'currency_id', 'company_id', 'date_invoice', 'type', 'percent_retention')
	def _amount_all_retention(self):
		for invoice in self:
			invoice.amount_retention = invoice.amount_untaxed * invoice.percent_retention / 100
			invoice.amount_to_pay = invoice.amount_total - invoice.amount_retention

	
	percent_retention = fields.Float(string='Retención (%)', digits=dp.get_precision('Discount'), default=0.0, readonly=True,
									  states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	amount_retention = fields.Monetary(string='Retención', store=True, readonly=True, compute='_amount_all_retention')
	amount_to_pay = fields.Monetary(string='Total a pagar', store=True, readonly=True, compute='_amount_all_retention')
	


	@api.model
	def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
		res = super(AccountInvoice, self)._prepare_refund(invoice, date_invoice, date,
														  description, journal_id)
		res.update({
			'percent_retention': self.percent_retention,
		})
		return res
