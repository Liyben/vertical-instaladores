# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class AccountInvoice(models.Model):
	_inherit = "account.move"

	def button_cancel(self):
		"""
		Inherit to update related picking as '2binvoiced' when the invoice is
		cancelled (only for invoices, not refunds)
		:return: bool
		"""
		result = super().button_cancel()
		pickings = self.filtered(
			lambda i: i.picking_ids and i.move_type in ["out_invoice", "in_invoice"]
		).mapped("picking_ids")
		pickings.set_sale_to_invoice_when_cancel()
		pickings.set_purchase_to_invoice_when_cancel()
		return result