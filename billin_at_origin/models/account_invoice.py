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

	def _compute_invoice_line_ids(self):
		for line in self.invoice_line_ids:
			#lines_ids = line.sale_line_ids.invoice_lines
			line.write({'invoice_line_ids': [(6, 0, line.sale_line_ids[0].invoice_lines)]})