# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):

	_inherit = 'sale.order.line'

	
	@api.onchange('total_lineales','total_cuadrados','manual_mode')
	def _onchange_metros(self):
		# Obtenemos el id de la unidad de medida ml y m2
		ml_id = self.env.ref('sale_order_line_sections.product_uom_lineal_meter').id
		m2_id = self.env.ref('sale_order_line_sections.product_uom_square_meter').id

		for material in self.task_materials_ids:
			# Comparamos el id de la unidad de medida del producto con ml_id
			if (material.material_id.uom_id.id == ml_id):
				material.quantity = self.total_lineales
			# Comparamos el id de la unidad de medida del producto con m2_id
			elif (material.material_id.uom_id.id == m2_id):
				material.quantity = self.total_cuadrados

	
	@api.onchange('total_lineales_manual','total_cuadrados_manual')
	def _onchange_metros_manual(self):
		# Obtenemos el id de la unidad de medida ml y m2
		ml_id = self.env.ref('sale_order_line_sections.product_uom_lineal_meter').id
		m2_id = self.env.ref('sale_order_line_sections.product_uom_square_meter').id

		for material in self.task_materials_ids:
			# Comparamos el id de la unidad de medida del producto con ml_id
			if (material.material_id.uom_id.id == ml_id):
				material.quantity = self.total_lineales_manual
			# Comparamos el id de la unidad de medida del producto con m2_id
			elif (material.material_id.uom_id.id == m2_id):
				material.quantity = self.total_cuadrados_manual
 