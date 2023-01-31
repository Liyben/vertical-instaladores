# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class ProductTemplate(models.Model):

	_inherit='product.template'

	#Check para indicar si se aplica la tarifa definida sobre la categoria del compuesto en los materiales y mano de obra de dicho compuesto
	apply_category = fields.Boolean(string='Aplicar tarifa del compuesto')
	