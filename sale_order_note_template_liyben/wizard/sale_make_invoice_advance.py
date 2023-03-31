# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class SaleAdvancePaymentInv(models.TransientModel):
	_inherit = "sale.advance.payment.inv"

	def _prepare_invoice_values(self, order, name, amount, so_line):
		res = super()._prepare_invoice_values(order, name, amount, so_line)
		if order.terms_template_id:
			res['narration'] = ''
		
		return res