# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	invoice_line_ids = fields.Many2many(
		'account.move.line',
		'invoice_line_origin_rel',
		'invoice_line_id', 'invoice_line_origin_id',
		string='Facturación a origen', readonly=True, copy=False,
		compute='_compute_invoice_line_ids')

	@api.depends('sale_line_ids.invoice_lines')
	def _compute_invoice_line_ids(self):
		for line in self:
			line.invoice_line_ids.ids = self.mapped('sale_line_ids').mapped('invoice_lines')