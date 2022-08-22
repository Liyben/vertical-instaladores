# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class SaleOrder(models.Model):
	_inherit = "sale.order"

	def _prepare_invoice(self):
		invoice_vals = super(SaleOrder, self)._prepare_invoice()

		if self.terms_template_id:
			invoice_vals.update({'terms_template_id': self.terms_template_id.id})

		return invoice_vals