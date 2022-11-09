# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

class ProductTemplate(models.Model):

	_inherit='product.template'

	# Plantilla
	is_template = fields.Boolean(string='Plantilla')
	
	