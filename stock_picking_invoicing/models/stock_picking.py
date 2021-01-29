# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockPicking(models.Model):
	_name = "stock.picking"
	_inherit = [
		_name,
		"stock.invoice.state.mixin",
	]

	@api.multi
	def set_to_be_invoiced(self):
		"""
		Update invoice_state of current pickings to "2binvoiced".
		:return: dict
		"""
		self._set_as_2binvoiced()
		return {}

	@api.multi
	def _set_as_2binvoiced(self):
		"""
		Inherit to also update related moves.
		:return: bool
		"""
		self.mapped("move_lines")._set_as_2binvoiced()
		return super(StockPicking, self)._set_as_2binvoiced()

	@api.multi
	def _set_as_invoiced(self):
		"""
		Inherit to also update related moves.
		:return: bool
		"""
		self.mapped("move_lines")._set_as_invoiced()
		return super(StockPicking, self)._set_as_invoiced()

	@api.multi
	def _get_partner_to_invoice(self):
		self.ensure_one()
		partner = self.partner_id
		return partner.address_get(['invoice']).get('invoice')

	@api.multi
	def button_validate(self):
		self.set_to_be_invoiced()
		return super(StockPicking, self).button_validate()

	@api.multi
	def set_sale_to_invoiced(self):
		for line in self:
			if line.sale_id:
				sale = line.sale_id
				sale.update({'invoice_status': 'invoiced'})

	@api.multi
	def set_purchase_to_invoiced(self):
		for line in self:
			if line.purchase_id:
				purchase = line.purchase_id
				purchase.update({'invoice_status': 'invoiced'})

	@api.multi
	def set_sale_to_invoice_when_cancel(self):
		for line in self:
			if line.sale_id:
				sale = line.sale_id
				sale.update({'invoice_status': 'to invoice'})
				if sale.order_line:
					for ol in sale.order_line:
						ol.update({'invoice_status': 'to invoice'})

	@api.multi
	def set_purchase_to_invoice_when_cancel(self):
		for line in self:
			if line.purchase_id:
				purchase = line.purchase_id
				purchase.update({'invoice_status': 'to invoice'})

	"""@api.multi
	def set_invoices_to_sale(self,invoices):
		if self.sale_id:
			sale = self.sale_id
			sale.update({'invoice_ids': [(6, 0, invoices.ids)]})

	@api.multi
	def set_invoices_to_purchase(self,invoices):
		if self.purchase_id:
			purchase = self.purchase_id
			purchase.update({'invoice_ids': [(6, 0, invoices.ids)]})"""