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
        
        if self.env.user.has_group('product_task_material_work.group_sales_merge_task_to_confirm'):
            return {'type': 'ir.actions.act_window',
                'name': _('Combinar partes de trabajo'),
                'res_model': 'sale.order.merge.task.wizard',
                'target': 'new',
                'view_id': self.env.ref('product_task_material_work.view_sale_order_merge_task').id,
                'view_mode': 'form'}
                
        return super().action_confirm()

    #Grupo cuenta analitica
    #account_analytic_group_id = fields.Many2one('account.analytic.group', string='Grupo', check_company=True) 

    #Método para los datos de la cuenta analitica
    """ def _prepare_analytic_account_data(self, prefix=None):
        analytic_account_vals = super(SaleOrder, self)._prepare_analytic_account_data(prefix)

        for order in self: 
            if order.account_analytic_group_id:
                analytic_account_vals.update({'group_id': order.account_analytic_group_id.id})

        return analytic_account_vals """

        
