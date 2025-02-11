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