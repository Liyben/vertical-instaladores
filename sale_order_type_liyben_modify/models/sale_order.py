# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	@api.multi
	@api.onchange('type_id')
	def onchange_type_id(self):
		super(SaleOrder, self).onchange_type_id()
		for order in self:
			if order.type_id.tax_id:
				for line in order.order_line:
					line.tax_id = line.order_id.type_id.tax_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
			else:
				for line in order.order_line:
					fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
					taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
					line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes

	
	@api.multi
	def _prepare_invoice(self):
		res = super(SaleOrder, self)._prepare_invoice()
		if self.type_id.account_id:
			res['account_id'] = self.type_id.account_id.id
		
		return res


class SaleOrderLine(models.Model):
	_inherit='sale.order.line'

	@api.multi
	def _prepare_invoice_line(self, qty):
		res = super(SaleOrderLine, self)._prepare_invoice_line(qty)

		if self.order_id.type_id.default_debit_account_id:
			res['account_id'] = self.order_id.type_id.default_debit_account_id.id

		return res

	@api.multi
	def _compute_tax_id(self):
		super(SaleOrderLine, self)._compute_tax_id()

		if self.order_id.type_id.tax_id:
			for line in self:
				line.tax_id = line.order_id.type_id.tax_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)