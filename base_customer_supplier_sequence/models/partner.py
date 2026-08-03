# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, models


class ResPartner(models.Model):
	"""Assigns 'ref' from a sequence on creation and copying"""

	_inherit = "res.partner"

	def _get_next_ref(self, vals=None):
		vals = vals or {}
		customer_rank = vals.get('customer_rank', self.customer_rank)
		supplier_rank = vals.get('supplier_rank', self.supplier_rank)
		if customer_rank:
			return self.env['ir.sequence'].next_by_code('res.partner.customer')
		elif supplier_rank:
			return self.env['ir.sequence'].next_by_code('res.partner.supplier')