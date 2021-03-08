# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
	_inherit = "account.invoice"

	@api.multi
	def action_cancel(self):
		"""
		Inherit to update related picking as '2binvoiced' when the invoice is
		cancelled (only for invoices, not refunds)
		:return: bool
		"""
		result = super(AccountInvoice, self).action_cancel()
		pickings = self.filtered(
			lambda i: i.picking_ids and
			i.type in ['out_invoice', 'in_invoice']).mapped("picking_ids")
		self.mapped("invoice_line_ids.move_line_ids")._set_as_2binvoiced()
		pickings._set_as_2binvoiced()
		# Ponemos el pedido de compra/venta como sin facturar
		pickings.set_sale_to_invoice_when_cancel()
		pickings.set_purchase_to_invoice_when_cancel()
		return result

	@api.multi
	def unlink(self):
		"""
		Inherit the unlink to update related picking as "2binvoiced"
		(only for invoices, not refunds)
		:return:
		"""
		pickings = self.filtered(
			lambda i: i.picking_ids and
			i.type in ['out_invoice', 'in_invoice']).mapped("picking_ids")
		self.mapped("invoice_line_ids.move_line_ids")._set_as_2binvoiced()
		pickings._set_as_2binvoiced()
		return super(AccountInvoice, self).unlink()

	@api.model
	def _prepare_refund(self, invoice, date_invoice=None, date=None,
						description=None, journal_id=None):
		"""
		Inherit to put link picking of the invoice into the new refund
		:param invoice: self recordset
		:param date_invoice: str
		:param date: str
		:param description: str
		:param journal_id: int
		:return: dict
		"""
		result = super(AccountInvoice, self)._prepare_refund(
			invoice=invoice, date_invoice=date_invoice, date=date,
			description=description, journal_id=journal_id)
		result.update({
			'picking_ids': [(6, False, invoice.picking_ids.ids)],
		})
		return result

	@api.model
	def create(self, vals):
		"""
		Inherit to update related picking as '2binvoiced' when the invoice is
		create from purchase order 
		:return: 
		"""
		invoice = super(AccountInvoice, self).create(vals)
		#Pedidos de compra asociados a las lineas de facturas
		purchase_ids = invoice.invoice_line_ids.mapped('purchase_id')
		#Albaranes asociados a a los pedidos de compra
		picking_ids = purchase_ids.mapped('picking_ids')
		#Albaranes en estado 'done'
		pickings = picking_ids.filtered(
			lambda p: p.state == 'done'
		)
		invoice.update({
			'picking_ids': [(6, False, pickings.ids)],
		})
		pickings._set_as_invoiced()

		return invoice


class AccountInvoiceLine(models.Model):
	_inherit = "account.invoice.line"

	@api.multi
	def unlink(self):
		
		records = self.filtered(lambda r: r.move_line_ids.picking_id).mapped("invoice_id.picking_ids")
		if records:
			records.write({
				'invoice_state': '2binvoiced',
			})

		self.mapped("move_line_ids")._set_as_2binvoiced()
		return super(AccountInvoiceLine, self).unlink()