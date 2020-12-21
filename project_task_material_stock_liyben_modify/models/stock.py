# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _


class StockMove(models.Model):
	_inherit = "stock.move"
	material_line_id = fields.Many2one('project.task.material', 'Linea de material en PT', ondelete='cascade', index=True)

	@api.model
	def _prepare_merge_moves_distinct_fields(self):
		distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
		distinct_fields.append('material_line_id')
		return distinct_fields

	@api.model
	def _prepare_merge_move_sort_method(self, move):
		move.ensure_one()
		keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
		keys_sorted.append(move.material_line_id.id)
		return keys_sorted

	def _action_done(self):
		result = super(StockMove, self)._action_done()
		for line in result.mapped('material_line_id').sudo():
			line.qty_delivered = line._get_delivered_qty()
		return result

	@api.multi
	def write(self, vals):
		res = super(StockMove, self).write(vals)
		if 'product_uom_qty' in vals:
			for move in self:
				if move.state == 'done':
					material_task_lines = self.filtered(lambda move: move.material_line_id and move.product_id.expense_policy in [False, 'no']).mapped('material_line_id')
					for line in material_task_lines.sudo():
						line.qty_delivered = line._get_delivered_qty()
				
		return res

	def _assign_picking_post_process(self, new=False):
		super(StockMove, self)._assign_picking_post_process(new=new)
		if new and self.material_line_id and self.material_line_id.task_id:
			self.picking_id.message_post_with_view(
				'mail.message_origin_link',
				values={'self': self.picking_id, 'origin': self.material_line_id.task_id},
				subtype_id=self.env.ref('mail.mt_note').id)

				
class ProcurementGroup(models.Model):
	_inherit = 'procurement.group'

	task_id = fields.Many2one('project.task', 'Parte de trabajo')


class ProcurementRule(models.Model):
	_inherit = 'procurement.rule'

	def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
		result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
		if values.get('material_line_id', False):
			result['material_line_id'] = values['material_line_id']
		return result


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	task_id = fields.Many2one(related="group_id.task_id", string="Partes de trabajo", store=True)