# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	
	@api.multi
	def action_run_purchase_order(self):
		self.mapped('move_lines')._action_cancel_no_unlink()
		self.write({'is_locked': True})
		self.btn_reset_to_draft()
		self.action_confirm()