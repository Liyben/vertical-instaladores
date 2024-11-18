# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    
    _inherit='sale.order'

    #Numero de cliente
    ref = fields.Char(related='partner_id.ref', store=True, string='Nº. Cliente', precompute=True)

    #Campos para el stock desde la tarea
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Tipo de operación",
        readonly=False,
        domain="[('company_id', '=', company_id)]",
        index=True,
        check_company=True,
        compute='_compute_stock_options', 
        store=True,
        precompute=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Ubicación de origen",
        readonly=False,
        check_company=True,
        index=True,
        compute='_compute_stock_options', 
        store=True,
        precompute=True,
    )
    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Ubicación destino",
        readonly=False,
        index=True,
        check_company=True,
        compute='_compute_stock_options', 
        store=True,
        precompute=True,
    )

    #Campo para el plan analitico
    plan_id = fields.Many2one(
        'account.analytic.plan',
        string='Plan analítico',
    )
    
    @api.depends('company_id')
    def _compute_stock_options(self):
        for order in self:
            default_picking_type_id = self.env['ir.default'].with_company(
                order.company_id.id)._get_model_defaults('sale.order').get('picking_type_id')
            default_location_id = self.env['ir.default'].with_company(
                order.company_id.id)._get_model_defaults('sale.order').get('location_id')
            default_location_dest_id = self.env['ir.default'].with_company(
                order.company_id.id)._get_model_defaults('sale.order').get('location_dest_id')
            
            picking_type = self.env.ref('product_task_material_work.stock_picking_type_task_material')

            if default_picking_type_id is not None:
                order.picking_type_id = default_picking_type_id
            else:
                order.picking_type_id = picking_type.id

            if default_location_id is not None:
                order.location_id = default_location_id
            else:
                order.location_id = picking_type.default_location_src_id.id

            if default_location_dest_id is not None:
                order.location_dest_id = default_location_dest_id
            else:
                order.location_dest_id = picking_type.default_location_dest_id.id

    def action_confirm(self):
        res = super().action_confirm()
        if self.env.user.has_group('product_task_material_work.group_sales_merge_task_to_confirm') and len(self.order_line.mapped('auto_create_task')) > 1:
            return {'type': 'ir.actions.act_window',
                'name': _('Combinar partes de trabajo'),
                'res_model': 'sale.order.merge.task.wizard',
                'target': 'new',
                'view_id': self.env.ref('product_task_material_work.view_sale_order_merge_task').id,
                'view_mode': 'form'}
                
        return res

    #Override función para los datos de la cuenta analitica
    def _prepare_analytic_account_data(self, prefix=None):
        """ Prepare SO analytic account creation values.

        :param str prefix: The prefix of the to-be-created analytic account name
        :return: `account.analytic.account` creation values
        :rtype: dict
        """
        self.ensure_one()
        name = self.name
        if prefix:
            name = prefix + ": " + self.name
        plan = self.plan_id
        if not plan:
            #plan = self.env['account.analytic.plan'].sudo().search([], limit=1)
            plan = self.env['account.analytic.plan'].sudo().create({
                'name': name,
            })
        return {
            'name': name,
            'code': self.client_order_ref,
            'company_id': self.company_id.id,
            'plan_id': plan.id,
            'partner_id': self.partner_id.id,
        }
