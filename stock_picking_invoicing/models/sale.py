# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp

class SaleOrder(models.Model):
	
	_inherit='sale.order'

	@api.multi
	def action_invoice_create(self, grouped=False, final=False):
		
		res = super().action_invoice_create(grouped, final)

		self.mapped("picking_ids")._set_as_invoiced()

		return res