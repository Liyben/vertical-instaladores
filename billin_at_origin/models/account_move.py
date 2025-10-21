# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_ids = fields.Many2many(
        'account.move',
        'invoice_origin_rel',
        'invoice_id', 'invoice_origin_id',
        string='Facturación a origen', readonly=True, copy=False, store=True,
        compute='_compute_invoice_ids',)

    @api.depends('invoice_line_ids.sale_line_ids.invoice_lines')
    def _compute_invoice_ids(self):
        for invoice in self:
            # Optimización: Navegamos relaciones en lugar de buscar
            # 1. De la factura (invoice) vamos a sus líneas (invoice_line_ids)
            # 2. De las líneas de factura vamos a las líneas de venta (sale_line_ids)
            # 3. De las líneas de venta vamos a los pedidos de venta (order_id)
            sale_orders = invoice.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
            
            # 4. De los pedidos de venta, obtenemos todas sus facturas (invoice_ids)
            # 5. Restamos la factura actual (invoice) del resultado
            invoice.invoice_ids = sale_orders.mapped('invoice_ids') - invoice