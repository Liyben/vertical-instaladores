# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_valuation = fields.Selection(selection_add=[
        ('only_analytic', 'Coste / Beneficio')
    ],  ondelete={
        'only_analytic': 'set default',
    })

    @api.onchange('property_valuation')
    def onchange_property_valuation_only_analytic(self):
        if self.property_valuation == 'only_analytic':
            self.property_stock_account_input_categ_id = False
            self.property_stock_account_output_categ_id = False
            self.property_stock_valuation_account_id = False