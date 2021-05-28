# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, exceptions, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta

class ProjectTask(models.Model):
	_inherit = 'project.task'

	picking_ids = fields.One2many('stock.picking', 'task_id', string='Albaranes')
	delivery_count = fields.Integer(string='Pedidos de entrega', compute='_compute_picking_ids')
	procurement_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False)

	@api.multi
	@api.depends('material_ids.stock_move_id')
	def _compute_stock_move(self):
		for task in self:
			task.stock_move_ids = task.mapped('material_ids.move_ids')
			
	@api.depends('picking_ids')
	def _compute_picking_ids(self):
		for task in self:
			task.delivery_count = len(task.picking_ids)

	#Devuelve los valores para la acción de ventana al pulsar en Entregas
	@api.multi
	def action_view_delivery(self):

		action = self.env.ref('stock.action_picking_tree_all').read()[0]

		pickings = self.mapped('picking_ids')
		if len(pickings) > 1:
			action['domain'] = [('id', 'in', pickings.ids)]
		elif pickings:
			action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
			action['res_id'] = pickings.id
		return action

	#Devuelve los valores para la acción de ventana al pulsar en Movimientos de stock
	def action_view_stock_move_lines(self):
		self.ensure_one()
		action = self.env.ref('stock.stock_move_action').read()[0]
		action['domain'] = [('analytic_account_id', '=', self.project_id.analytic_account_id.id)]
		return action
			
	@api.multi
	def write(self, vals):
		res = super(ProjectTask, self).write(vals)
		for task in self:
			if task.analytic_line_ids:
				task.mapped('analytic_line_ids').unlink()

			if 'stage_id' in vals or 'material_ids' in vals:
				if task.stage_id.consume_material:
					todo_lines = task.material_ids.filtered(
						lambda m: not m.move_ids
					)
					if todo_lines:
						#todo_lines.unlink_stock_move()
						todo_lines.create_stock_move()
						#todo_lines.create_analytic_line()

				else:
					if task.unlink_stock_move():
						if task.material_ids.mapped(
								'analytic_line_id'):
							raise exceptions.Warning(
								_("You can't move to a not consume stage if "
								  "there are already analytic lines")
							)
					task.material_ids.mapped('analytic_line_id').unlink()
		return res

class ProjectTaskMaterial(models.Model):
	_inherit = 'project.task.material'

	move_ids = fields.One2many('stock.move', 'material_line_id', string='Movimientos de stock')
	#initial_quantity = fields.Float(string='Quantity')
	#add_quantity = fields.Float(string='Quantity')

	def _prepare_stock_move(self):
		product = self.product_id
		res = {
			'product_id': product.id,
			'name': product.partner_ref,
			'state': 'confirmed',
			'product_uom': self.product_uom_id.id or product.uom_id.id,
			'product_uom_qty': self.quantity,
			'origin': self.task_id.sale_line_id.order_id.name +' ('+ self.task_id.code + ')',
			'location_id':
				self.task_id.location_source_id.id or
				self.task_id.project_id.location_source_id.id or
				self.env.ref('stock.stock_location_stock').id,
			'location_dest_id':
				self.task_id.location_dest_id.id or
				self.task_id.project_id.location_dest_id.id or
				self.env.ref('stock.stock_location_customers').id,
		}
		return res

	@api.multi
	def create_stock_move(self):
		pick_type = self.env.ref(
			'project_task_material_stock.project_task_material_picking_type')

		task = self[0].task_id

		analytic_account_id = task.project_id.analytic_account_id

		group_id = task.procurement_group_id
		if not group_id:
			group_id = self.env['procurement.group'].create({
					'name': task.sale_line_id.order_id.name +' ('+ task.code + ')', 'move_type': task.sale_line_id.order_id.picking_policy or 'direct',
					'task_id': task.id,
					'sale_id': task.sale_line_id.order_id.id or False,
					'partner_id': task.partner_id.id,
				})
			task.procurement_group_id = group_id.id

		picking_id = task.picking_id or self.env['stock.picking'].create({
			'origin': "{} ({})".format(task.sale_line_id.order_id.name, task.code),
			'partner_id': task.partner_id.id,
			'picking_type_id': pick_type.id,
			'location_id': pick_type.default_location_src_id.id,
			'location_dest_id': pick_type.default_location_dest_id.id,
		})
		if not task.picking_ids:
			list_picking = []
			list_picking.append(picking_id.id)

		for line in self:
			if not line.move_ids:
				list_ids=[]
				move_vals = line._prepare_stock_move()
				move_vals.update({
					'picking_id': picking_id.id or False,
					'group_id': group_id.id or False,
					'analytic_account_id' : analytic_account_id.id or False,
					})
				move_id = self.env['stock.move'].create(move_vals)
				list_ids.append(move_id.id)
				line.move_ids = list_ids
			
	@api.multi
	def _get_delivered_qty(self):
		self.ensure_one()
		qty = 0.0
		for move in self.move_ids.filtered(lambda r: r.state == 'done' and not r.scrapped):
			if move.location_dest_id.usage == "customer":
				if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
					qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom_id or self.product_id.uom_id)
			elif move.location_dest_id.usage != "customer" and move.to_refund:
				qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom_id or self.product_id.uom_id)
		return qty

	@api.multi
	def unlink(self):
		self.mapped('move_ids')._action_cancel()
		self.with_context(prefetch_fields=False).mapped('move_ids').unlink()
		return super(ProjectTaskMaterial, self).unlink()
