# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_order_count = fields.Integer(
        string="Número de Pedidos de Compra",
        compute='_compute_purchase_order_count',
        groups='stock.group_stock_user',
        store=True
    )

    #@api.depends('group_id','move_ids.purchase_line_id')
    def _compute_purchase_order_count(self):
        for pick in self:
            # Verificar si hay group_id 
            if not pick.group_id:
                pick.purchase_order_count = 0
            else:
                pick.purchase_order_count = len(pick._get_purchase_orders())

    def _get_purchase_orders(self):
        """Devuelve los pedidos de compra asociados al grupo de abastecimiento."""
        self.ensure_one()
        return self.env['purchase.order'].search([('group_id', '=', self.group_id.id)])
    
    def action_view_purchase_order(self):
        self.ensure_one()
        purchase_orders = self._get_purchase_orders()
        
        # Estructura base de la acción
        action = {
            'name': _("Pedidos de Compra"),
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'context': {'create': False}, # Evita crear pedidos desde esta vista
        }

        if len(purchase_orders) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': purchase_orders.id,
            })
        else:
            action.update({
                'name': _("Pedidos de Compra generados desde %s") % self.name,
                'domain': [('id', 'in', purchase_orders.ids)],
                'view_mode': 'tree,form',
            })
        
        return action