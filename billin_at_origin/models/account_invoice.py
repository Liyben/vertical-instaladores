# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

""" import logging

from stock_picking_invoicing_lyb_mod.models.sale import SaleOrder
_logger = logging.getLogger(__name__) """

class AccountMove(models.Model):
	_inherit = "account.move"

	invoice_ids = fields.Many2many(
		'account.move',
		'invoice_origin_rel',
		'invoice_id', 'invoice_origin_id',
		string='Facturación a origen', readonly=True, copy=False, store=True,
		compute='_compute_invoice_ids')

	@api.depends('invoice_line_ids.sale_line_ids.invoice_lines')
	def _compute_invoice_ids(self):
		SaleOrder = self.env["sale.order"]
		for invoice in self:
			sale_orders = SaleOrder.search([("invoice_ids", "=", invoice.id)])
			invoice.invoice_ids = sale_orders.mapped('invoice_ids') - invoice

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	invoice_line_ids = fields.Many2many(
		'account.move.line',
		'invoice_line_origin_rel',
		'invoice_line_id', 'invoice_line_origin_id',
		string='Facturación a origen', readonly=True, copy=False, store=True,
		compute='_compute_invoice_line_ids')

	@api.depends('sale_line_ids.invoice_lines')
	def _compute_invoice_line_ids(self):
		SaleOrderLine = self.env["sale.order.line"]
		for line in self:
			sale_lines = SaleOrderLine.search([("invoice_lines", "=", line.id)])
			line.invoice_line_ids = sale_lines.mapped('invoice_lines') - line
			#line.invoice_line_ids = self.mapped('sale_line_ids').mapped('invoice_lines') - line