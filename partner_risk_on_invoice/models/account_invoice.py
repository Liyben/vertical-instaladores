# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class AccountMove(models.Model):
	_inherit = "account.move"


	@api.depends('partner_id', 'partner_id.name', 'partner_id.insurance_credit_limit')
	def _compute_credit_limit(self):
		for invoice in self:
			
			invoice.partner_risk_credit_limit = invoice.partner_id.name + " - (Riesgo: " + str(invoice.partner_id.insurance_credit_limit) + " €)"
			invoice.insurance_credit_limit = invoice.partner_id.insurance_credit_limit

	
	
	partner_risk_credit_limit = fields.Char(string='Cliente con Riesgo', store=True, readonly=True, compute='_compute_credit_limit')
	insurance_credit_limit = fields.Float(string='Límite de crédito del seguro', store=True, readonly=True, compute='_compute_credit_limit')
	
