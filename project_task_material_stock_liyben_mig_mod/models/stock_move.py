# Copyright 2019 Valentin Vinagre <valentin.vinagre@qubiq.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, fields, models, _
from odoo.tools.sql import column_exists, create_column


class StockMove(models.Model):
    _inherit = "stock.move"

    task_material_id = fields.One2many(
        "project.task.material",
        "stock_move_id",
        string="Project Task Material",
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('task_material_id')
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.task_material_id.ids)
        return keys_sorted

    def _assign_picking_post_process(self, new=False):
        super(StockMove, self)._assign_picking_post_process(new=new)
        if new and self.task_material_id:
            picking_id = self.mapped('picking_id')
            task_material_ids = self.mapped('task_material_id')
            for material_id in task_material_ids:
                picking_id.message_post_with_view(
                    'mail.message_origin_link',
                    values={'self': picking_id, 'origin': material_id.task_id},
                    subtype_id=self.env.ref('mail.mt_note').id)

    def _action_done(self, cancel_backorder=False):
        # The analytical amount is updated with the value of the
        # stock movement, because if the product has a tracking by
        # lot / serial number, the cost when creating the
        # analytical line is not correct.
        res = super()._action_done(cancel_backorder=cancel_backorder)
        self.mapped("task_material_id")._update_unit_amount()
        return res

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    task_id = fields.Many2one('project.task', 'Parte de trabajo')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['task_material_id']
        return fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    task_id = fields.Many2one(related="group_id.task_id", string="Partes de trabajo", store=True)

    def _auto_init(self):
        if not column_exists(self.env.cr, 'stock_picking', 'task_id'):
            create_column(self.env.cr, 'stock_picking', 'task_id', 'int4')
        return super()._auto_init()
