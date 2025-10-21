# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_line_ids = fields.Many2many(
        'account.move.line',
        'invoice_line_origin_rel',
        'invoice_line_id', 'invoice_line_origin_id',
        string='Facturación a origen', readonly=True, copy=False, store=True,
        compute='_compute_invoice_line_ids',)

    @api.depends('sale_line_ids.invoice_lines')
    def _compute_invoice_line_ids(self):
        for line in self:
            # Optimización: Navegamos relaciones en lugar de buscar
            # 1. De la línea de factura (line) vamos a sus líneas de venta (sale_line_ids)
            # 2. De las líneas de venta, obtenemos todas sus líneas de factura (invoice_lines)
            related_lines = line.sale_line_ids.mapped('invoice_lines')
            
            # 3. Restamos la línea de factura actual (line) del resultado
            line.invoice_line_ids = related_lines - line