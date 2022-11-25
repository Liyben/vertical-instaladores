# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

class SaleOrder(models.Model):

	_inherit='sale.order'


	# % desperdicio
	can_be_confirmed = fields.Boolean(compute = '_compute_can_be_confirmed')


	@api.depends('order_line','order_line.product_id')
	def _compute_can_be_confirmed(self):
		for record in self:
			record.can_be_confirmed = False
			for line in record.order_line:
				record.can_be_confirmed = record.can_be_confirmed or line.product_id.is_template
				for material in line.task_materials_ids:
					record.can_be_confirmed = record.can_be_confirmed or material.material_id.is_template
