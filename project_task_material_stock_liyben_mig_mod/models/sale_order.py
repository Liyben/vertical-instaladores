# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class SaleOrder(models.Model):

	_inherit='sale.order'

	def _get_purchase_orders(self):
		purchases = []
		result = super(SaleOrder, self)._get_purchase_orders()
		tasks = self.mapped('tasks_ids')
		if len(tasks) >= 1:
			purchases = self.env['purchase.order'].search([('group_id', 'in', tasks.mapped('procurement_group_id').ids)])
		if result and purchases:
			return result | purchases
		elif result:
			return result
		elif purchases:
			return purchases
		