# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class ProductTemplate(models.Model):

	_inherit='product.template'

	# Concatenar
	concatenate_description = fields.Boolean(string='Concatenar descripción')