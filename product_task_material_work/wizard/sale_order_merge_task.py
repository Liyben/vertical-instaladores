# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SaleOrderMergeTaskWizard(models.TransientModel):
    _name = 'sale.order.merge.task.wizard'
    _description = "Combinar partes de trabajo desde presupuesto"

    #sale_order_id = fields.Many2one(
    #    'sale.order', default=lambda self: self.env.context.get('active_id'), required=True)
        
    #No Combina los PTs
    def action_confirm(self):
        self.ensure_one()
        order = self.env['sale.order'].browse(self._context.get('active_id'))

        #Confirmamos el presupuesto sin combinar
        return order.action_confirm()
        _logger.debug("Task: %s", str(order.tasks_ids.ids))

    #Combina los PTs
    def merge_task(self):
        #self.ensure_one()
        _logger.debug("Order: %s", str(self.sale_order_id.id))
        #Confirmamos el presupuesto
        self.sale_order_id.action_confirm()

        #Comprobamos el control de facturación de los productos compuestos
        list_bool = []
        for line in self.sale_order_id.order_line:
            if line.auto_create_task:
                list_bool.append(line.product_id.invoicing_finished_task)
        if any(list_bool) == True and all(list_bool) == False:
            raise UserError(_('Para combinar partes de trabajo todos deben de tener el mismo control de facturas.\n'+
            'Si desea unificar todas las tareas, siga estos pasos:\n'+
            '1. Cancelar presupuesto.\n'+
            '2. Configurar todos los productos con el mismo control de factura.\n'+
            '3. Vuelva al prespuesto, conviertalo a presupuesto y confirmelo.\n'))
        
        current_tasks = self.env['project.task'].browse(self.sale_order_id.tasks_ids.ids)
        _logger.debug("Task: %s", str(self.sale_order_id.tasks_ids.ids))
        planned_hours = 0
        timesheets = self.env['account.analytic.line']
        works_ids = self.env['project.task.work']
        stock_ids = self.env['stock.move']
        tags = self.env['project.tags']
        projects = current_tasks.mapped('project_id')
        description = ''
        works = ''

        if len(projects) > 1:
            raise ValidationError('Las tareas deben pertenecer al mismo proyecto!!')

        for task in current_tasks:
            planned_hours += task.allocated_hours
            timesheets += task.timesheet_ids
            works_ids += task.task_works_ids
            stock_ids += task.move_ids
            tags += task.tag_ids

            if task.description:
                description += "<b>%s</b>:<br/>%s" % (task.name, task.description or 'Sin descripción.')

            if task.work_to_do:
                works += "Trabajo a realizar para el PT <b>%s</b>:<br/>%s" % (task.name, task.work_to_do or 'Sin trabajo a realizar')

        #Creacion tarea
        task_id = self.create({
            'allocated_hours': planned_hours,
            'project_id': projects.id if projects else False,
            'analytic_account_id': projects.analytic_account_id.id if projects else False,
            'partner_id': self.sale_order_id.partner_id.id,
            'user_ids': False,
            'sale_line_id': self.sale_order_id.tasks_ids[0].sale_line_id.id,
            'sale_order_id': self.sale_order_id.id,
            'company_id': projects.company_id.id if projects else False,
            'oppor_id': self.sale_order_id.opportunity_id.id or False, 
            'description': description,
            'work_to_do': works,
            'tag_ids': [(6, 0, tags.ids)] if tags else False,
            'name': ', '.join(current_tasks.mapped('name')),
            'timesheet_ids': [(6, 0, timesheets.ids)] if timesheets else False,
            'task_works_ids': [(6, 0, works_ids.ids)] if works_ids else False,
            'move_ids': [(6, 0, stock_ids.ids)] if stock_ids else False,
            'merge_task_ids': [(6, 0, current_tasks.ids)]
        })

        #Tareas fusionadas se archivan
        current_tasks.write({'active': False})

        #Se añade la lista de tareas fusionadas al chatter
        comment_subtype_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')
        task_id.message_post_with_source(
            'product_task_material_work.mail_template_task_merge',
            render_values={'tasks': current_tasks},
            subtype_id=comment_subtype_id
        )

        #Se muestra la tarea resultante
        return {
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': task_id.id,
        }

    