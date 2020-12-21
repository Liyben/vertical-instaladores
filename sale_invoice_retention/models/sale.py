# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp

class SaleOrder(models.Model):
	
	_inherit='sale.order'

	@api.depends('order_line.price_total', 'percent_retention')
	def _amount_all_retention(self):
		for order in self:
			order.amount_retention = order.amount_untaxed * order.percent_retention / 100
			order.amount_to_pay = order.amount_total - order.amount_retention

			
	percent_retention = fields.Float(string='Retención (%)', digits=dp.get_precision('Discount'), default=0.0, readonly=True,
									  states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
	amount_retention = fields.Monetary(string='Retención', store=True, readonly=True, compute='_amount_all_retention', help="Retención Total.")
	amount_to_pay = fields.Monetary(string='Total a pagar', store=True, readonly=True, compute='_amount_all_retention', help="Total a pagar.")


	@api.multi
	def _prepare_invoice(self):
		invoice_vals = super(SaleOrder, self)._prepare_invoice()
		invoice_vals.update({
			'percent_retention': self.percent_retention,
		})
		return invoice_vals