# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class SaleOrder(models.Model):

	_inherit='sale.order'

	def _get_purchase_orders(self):
		return self.env['purchase.order'].search(['|', ('group_id', 'in', self.tasks_ids.procurement_group_id.id), ('id', 'in', self.order_line.purchase_line_ids.order_id)])
		