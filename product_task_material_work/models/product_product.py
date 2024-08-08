# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class ProductProduct(models.Model):

	_inherit='product.product'

	#Función que recalcula el precio de venta y coste del articulo partida a partir de los totales de venta y coste	
	def product_action_recalculate(self):
		self.list_price = 0.0
		self.standard_price = 0.0
		for record in self:
			record.list_price = record.total_sp_work + record.total_sp_material
			record.standard_price = record.total_cp_work + record.total_cp_material

	#Devuelve los valores para la acción de ventana al pulsar en Productos Compuestos
	def action_view_product_compound(self):

		action = self.env.ref('sale.product_template_action').read()[0]

		products_compound = []
		if self.type == 'service':
			works = self.env["product.task.work"].search([("work_id.product_tmpl_id", "=", self.id)])
			products_compound = works.mapped('product_id')
		else: 
			materials = self.env["product.task.material"].search([("material_id.product_tmpl_id", "=", self.id)])
			products_compound = materials.mapped('product_id')

		if len(products_compound) > 1:
			action['views'] = [(self.env.ref('product.product_template_tree_view').id, 'tree'),(self.env.ref('product.product_template_form_view').id, 'form')]
			action['domain'] = [('id', 'in', products_compound.ids)]
		elif products_compound:
			action['views'] = [(self.env.ref('product.product_template_form_view').id, 'form')]
			action['res_id'] = products_compound.id
		return action
			
