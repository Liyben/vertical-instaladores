# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockPicking(models.Model):
	_name = "stock.picking"
	_inherit = [
		_name,
		"stock.invoice.state.mixin",
	]

	def set_sale_to_invoiced(self):
		for line in self:
			if line.sale_id:
				sale = line.sale_id
				sale.update({'invoice_status': 'invoiced'})

	def set_purchase_to_invoiced(self):
		for line in self:
			if line.purchase_id:
				purchase = line.purchase_id
				purchase.update({'invoice_status': 'invoiced'})

	def set_sale_to_invoice_when_cancel(self):
		for line in self:
			if line.sale_id:
				sale = line.sale_id
				sale.update({'invoice_status': 'to invoice'})
				if sale.order_line:
					for ol in sale.order_line:
						ol.update({'invoice_status': 'to invoice'})

	def set_purchase_to_invoice_when_cancel(self):
		for line in self:
			if line.purchase_id:
				purchase = line.purchase_id
				purchase.update({'invoice_status': 'to invoice'})