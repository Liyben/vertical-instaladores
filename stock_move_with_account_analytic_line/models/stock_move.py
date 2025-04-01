# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for rec in self:
            if (rec.product_id
                and rec.product_id.type != "service"
                and rec.product_id.categ_id.property_valuation == "only_analytic"
                and rec.picking_id
                and rec.picking_id.analytic_distribution
                and rec.task_id
                and rec.state == "done"
            ):
                unit_amount = rec.quantity_done
                amount = 0.0 - rec.product_id.standard_price 
                if rec.location_id and rec.location_id.usage == "customer":
                    amount *= -1.0

                analytic_line_vals = self.env['account.analytic.account']._perform_analytic_distribution(rec.analytic_distribution, amount, unit_amount, rec.analytic_account_line_ids, rec)
                #_logger.debug("AL: %s\n", str(analytic_line_vals))
                if analytic_line_vals:    
                    rec.analytic_account_line_ids += self.env['account.analytic.line'].sudo().create(analytic_line_vals)
        return res
   