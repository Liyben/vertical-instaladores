# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, exceptions, _


class ProductTemplate(models.Model):
	_inherit = "product.template"

	@api.onchange('invoicing_finished_task')
	def _onchange_material_id(self):
		for record in self:
			record.invoice_policy = 'order'
	