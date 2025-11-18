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
                and rec.picking_id.analytic_account_id
                and rec.picking_id.picking_type_id.stock_move_from_task
                and rec.state == "done"
            ):
                analytic_line_vals = self._prepare_analytic_line(rec)
                #_logger.debug("AL: %s\n", str(analytic_line_vals))
                if analytic_line_vals:    
                    self.env['account.analytic.line'].create(analytic_line_vals)
        return res
    
    def _prepare_analytic_line(self, move):
        amount = 0.0 - (move.quantity_done * move.product_id.standard_price) 
        if move.location_id and move.location_id.usage == "customer":
            amount *= -1.0
        #_logger.debug("amount: %s\n", str(amount))
        return {
                'name': "{} - {}".format(move.reference, move.product_id.name),
                'date': fields.date.today(),
                'account_id': move.analytic_account_id.id,
                'group_id': move.analytic_account_id.group_id.id,
                'unit_amount': move.quantity_done,
                'product_id': move.product_id and move.product_id.id or False,
                'product_uom_id': move.product_uom and move.product_uom.id or False,
                'amount': amount,
                'general_account_id': self.env.ref('l10n_es.1_account_common_300').id or False,
                'ref': "{} - {}".format(move.reference, move.product_id.name),
                'user_id': self._uid,
                'partner_id': move.partner_id.id,
                'company_id': move.analytic_account_id.company_id.id or move.company_id.id,
            }