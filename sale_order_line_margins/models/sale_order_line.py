# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin_benefit = fields.Float(
        string='Margen', 
        digits='Discount',
        )
    
    @api.onchange('product_id')
    def _onchange_product_id_change_margin_benefit(self):

        for line in self:
            line.margin_benefit = 0.0

    @api.onchange('margin_benefit','purchase_price')
    def _onchange_margin_benefit(self):
        
        for line in self:
            if line.margin_benefit != 0.0:
                line = line.with_company(line.company_id)
                price = line.purchase_price / (1-(line.margin_benefit / 100))
                line.price_unit = line._convert_to_sol_currency(
                    price,
                    line.product_id.cost_currency_id)
            else: 
                line._compute_price_unit()