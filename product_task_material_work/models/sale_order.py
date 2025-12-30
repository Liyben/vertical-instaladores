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
        res = super().action_confirm()
        if self.env.user.has_group('product_task_material_work.group_sales_merge_task_to_confirm') and len(self.order_line.mapped('auto_create_task')) > 1:
            return {'type': 'ir.actions.act_window',
                'name': _('Combinar partes de trabajo'),
                'res_model': 'sale.order.merge.task.wizard',
                'target': 'new',
                'view_id': self.env.ref('product_task_material_work.view_sale_order_merge_task').id,
                'view_mode': 'form'}
                
        return res

    #Se añade la cuenta anañitica a la distribución analitica de cada linea despues de crearla
    def _create_analytic_account(self, prefix=None):
        result = super(SaleOrder, self)._create_analytic_account(prefix=prefix)
        for order in self:
            analytic_account_id = order.analytic_account_id.id
            if analytic_account_id:
                analytic_account_id = str(analytic_account_id)
                for line in order.order_line:
                    line.analytic_distribution = {analytic_account_id: 100}
        return result
    
    def get_report_sections_grouped(self, lines_to_report):
        """
        Recibe las líneas del reporte (ya filtradas por Odoo) y las agrupa por sección.
        Devuelve una lista de diccionarios:
        [
            {
                'section_line': record(sale.order.line) o False (para líneas sin sección),
                'lines': recordset(sale.order.line), # Los productos de esta sección
                'pagebreak': Boolean,
                'subtotal': Float,
            },
            ...
        ]
        """
        groups = []
        current_group = {
            'section_line': self.env['sale.order.line'], # Vacío por defecto
            'lines': [],
            'pagebreak': False,
            'subtotal': 0.0,
        }

        for line in lines_to_report:
            if line.display_type == 'line_section':
                # 1. Si ya teníamos un grupo acumulado con contenido, lo guardamos
                if current_group['lines'] or current_group['section_line']:
                    groups.append(current_group)
                
                # 2. Iniciamos un nuevo grupo basado en esta sección
                current_group = {
                    'section_line': line,
                    'lines': [],
                    # Usamos el campo de tu módulo 'sale_order_line_layout'
                    'pagebreak': line.layout_category_id.pagebreak, 
                    'subtotal': 0.0,
                }
            elif line.display_type == 'line_note':
                # Las notas se añaden al grupo actual
                current_group['lines'].append(line)
            else:
                # Productos normales
                current_group['lines'].append(line)
                current_group['subtotal'] += line.price_subtotal

        # 3. No olvidar añadir el último grupo acumulado al final del bucle
        if current_group['lines'] or current_group['section_line']:
            groups.append(current_group)

        return groups