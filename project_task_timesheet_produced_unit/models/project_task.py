# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
import json

class Task(models.Model):
	_inherit = "project.task"

	product_id_domain = fields.Char(
	compute="_compute_product_id_domain",
	readonly=True,
	store=False,
)

	@api.depends('material_ids')
	def _compute_product_id_domain(self):
		for record in self:
			#record.product_id_domain = json.dumps([])
			if record.material_ids:
				ids = record.material_ids.mapped('product_id').ids
				record.product_id_domain = json.dumps([('id', 'in', ids)])