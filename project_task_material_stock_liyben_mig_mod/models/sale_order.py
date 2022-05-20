# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):

	_inherit='sale.order'

	def _get_purchase_orders(self):
		result = super(SaleOrder, self)._get_purchase_orders()
		_logger.debug('RESULT OF SUPER %s', result)
		""" tasks = self.mappped('tasks_ids')
		if len(tasks) >= 1:
			return self.env['purchase.order'].search([('group_id', 'in', self.tasks_ids.procurement_group_id.id)]) """
		