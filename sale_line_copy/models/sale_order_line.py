# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _, exceptions

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	def sale_order_line_copy(self):
		
		if self.order_id.state == 'draft':
			self.copy(default={'order_id':self.order_id.id, 'sequence':self.sequence+1})
		else:
			raise exceptions.ValidationError(_('Error!'), _("Este pedido no está en borrador."))