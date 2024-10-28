# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class AccountMove(models.Model):

	_inherit='account.move'

	#Numero de cliente
	customer_code = fields.Char(related='partner_id.ref', readonly=True, string='Nº. Cliente')
	#Linea de factura con algun producto tipo compuesto
	has_compound_product = fields.Boolean(string='Tiene productos compuestos', compute='_compute_has_compound_product')
	
	#Calcula si la factura tiene algun producto tipo compuesto
	@api.depends('invoice_line_ids', 'invoice_line_ids.auto_create_task')
	def _compute_has_compound_product(self):
		for invoice in self:
			invoice.has_compound_product = False
			for line in invoice.invoice_line_ids:
				if line.auto_create_task:
					invoice.has_compound_product = True
	
	#Balancea las lineas de la factura asociada
	""" def recompute_balance(self):
		for invoice in self.with_context(check_move_validity=False):
			invoice.line_ids._onchange_price_subtotal()
			invoice._recompute_dynamic_lines(recompute_all_taxes=True) """
			

	