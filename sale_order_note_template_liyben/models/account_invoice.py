# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class AccountMove(models.Model):
	_inherit = "account.move"


	narration = fields.Html()
	terms_template_id = fields.Many2one(
		"sale.terms_template",
		string="Terms and conditions template",
		readonly=True,
		states={"draft": [("readonly", False)]},
	)

	@api.onchange("terms_template_id")
	def _onchange_terms_template_id(self):
		if self.terms_template_id:
			self.narration = self.terms_template_id.get_value(self)

