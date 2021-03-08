# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class StockBackorderConfirmation(models.TransientModel):
	_inherit = 'stock.backorder.confirmation'
	_description = 'Backorder Confirmation'

	@api.one
	def _process(self, cancel_backorder=False):
		self.pick_ids.set_to_be_invoiced()
		self.pick_ids.set_sale_to_invoiced()
		self.pick_ids.set_purchase_to_invoiced()
		return super(StockBackorderConfirmation, self)._process()