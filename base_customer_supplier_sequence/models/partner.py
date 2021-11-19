# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, models


class Partner(models.Model):

	"""Assigns 'ref' from a sequence on creation and copying"""
	inherit = "res.partner"

	def _get_next_ref(self, vals=None):
		if vals.get('customer_rank'):
			return self.env['ir.sequence'].next_by_code('res.partner.customer')
		elif vals.get('supplier_rank'):
			return self.env['ir.sequence'].next_by_code('res.partner.supplier')