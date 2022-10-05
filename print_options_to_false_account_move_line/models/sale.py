# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class SaleOrderLine(models.Model):

	_inherit='sale.order.line'

	def _prepare_invoice_line(self, **optional_values):
		res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)

		if res:
			res['detailed_time'] = False
			res['detailed_price_time'] = False
			res['detailed_materials'] = False
			res['detailed_price_materials'] = False
			res['detailed_subtotal_price_time'] = False
			res['detailed_subtotal_price_materials'] = False

		return res