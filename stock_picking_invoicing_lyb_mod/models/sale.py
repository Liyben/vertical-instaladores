# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class SaleOrder(models.Model):
	
	_inherit='sale.order'

	def _create_invoices(self, grouped=False, final=False, date=None):
		"""
		Create the invoice associated to the SO.
		:param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
						(partner_invoice_id, currency)
		:param final: if True, refunds will be generated if necessary
		:returns: list of created invoices
		"""
		
		res = super()._create_invoices(grouped, final, date)

		self.mapped("picking_ids")._set_as_invoiced()

		return res