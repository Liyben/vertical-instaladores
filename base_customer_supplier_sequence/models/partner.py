# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, models


class ResPartner(models.Model):

	"""Assigns 'ref' from a sequence on creation and copying"""

	def _get_next_ref(self, vals=None):
		if vals.get('customer'):
			return self.env['ir.sequence'].next_by_code('res.partner.customer')
		elif vals.get('supplier'):
			return self.env['ir.sequence'].next_by_code('res.partner.supplier')