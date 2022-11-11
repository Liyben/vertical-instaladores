# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _

class ProductProduct(models.Model):

	_inherit='product.product'

	cost_produced_unit = fields.Float(
		'Coste Unit-P', company_dependent=True,
        digits='Product Price',
        groups="base.group_user",
	)



class ProductTemplate(models.Model):

	_inherit='product.template'

	cost_produced_unit = fields.Float(
		'Coste Unit-P', compute='_compute_cost_produced_unit',
		inverse='_set_cost_produced_unit', search='_search_cost_produced_unit',
		digits='Product Price', groups="base.group_user",
	)
	
	@api.depends_context('company')
	@api.depends('product_variant_ids', 'product_variant_ids.cost_produced_unit')
	def _compute_cost_produced_unit(self):
		unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
		for template in unique_variants:
			template.cost_produced_unit = template.product_variant_ids.cost_produced_unit
		for template in (self - unique_variants):
			template.cost_produced_unit = 0.0

	def _set_cost_produced_unit(self):
		for template in self:
			if len(template.product_variant_ids) == 1:
				template.product_variant_ids.cost_produced_unit = template.cost_produced_unit

	def _search_cost_produced_unit(self, operator, value):
		products = self.env['product.product'].search([('cost_produced_unit', operator, value)], limit=None)
		return [('id', 'in', products.mapped('product_tmpl_id').ids)]