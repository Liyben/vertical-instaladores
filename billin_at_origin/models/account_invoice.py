# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	invoice_line_ids = fields.Many2many(
		'account.move.line',
		'invoice_line_origin_rel',
		'invoice_line_id', 'invoice_line_origin_id',
		string='Facturación a origen', readonly=True, copy=False)