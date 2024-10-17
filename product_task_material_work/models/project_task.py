# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProjectTask(models.Model):
    _inherit = 'project.task'

    #Trabajo a realizar
    work_to_do = fields.Html(string='Trabajo a realizar')

    #Opportunidad / Aviso
    oppor_id = fields.Many2one(comodel_name='crm.lead', string='Oportunidad / Aviso')

    #Fecha tarea
    date_task = fields.Datetime(string='Fecha tarea', required=True, copy=False, default=fields.Datetime.now)

    #Tareas unificadas
    merge_task_ids = fields.Many2many('project.task','merge_tasks','task_id','merge_task_id','Tareas unificadas')
    merge_task_count = fields.Integer('Tareas unificadas',compute='compute_merge_task_count')

    #Campos para la firma
    signature = fields.Binary(string="Firma", copy=False, tracking=1)
    signed_by = fields.Char(string="Firmada por", copy=False, tracking=2)
    signed_on = fields.Datetime(string="Firmada en", copy=False, tracking=3)

    def compute_merge_task_count(self):
        for task_id in self:
            task_id.merge_task_count = len(task_id.merge_task_ids)

    def action_merge_tasks(self):
        self.ensure_one()
        action = {
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
        }
        if len(self.merge_task_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.merge_task_ids.id,
            })
        else:
            action.update({
                'domain': [('id', 'in', self.merge_task_ids.ids)],
                'view_mode': 'tree,form',
            })
        return action

    def task_merge(self):
        current_tasks = self.env['project.task'].browse(self._context.get('active_ids'))
        planned_hours = 0
        timesheets = self.env['account.analytic.line']
        tags = self.env['project.tags']
        projects = current_tasks.mapped('project_id')
        #project_id = None
        description = ''
        works = ''
        #deadline_date = None
        if len(projects) > 1:
            raise ValidationError('Las tareas deben pertenecer al mismo proyecto!!')
        if len(current_tasks) <= 1:
            raise ValidationError('Selecciona al menos dos tareas para poder unificarlas.')
        for task in current_tasks:
            #project_id = task.project_id.id
            planned_hours += task.allocated_hours
            #deadline_date = task.date_deadline
            timesheets += task.timesheet_ids
            tags += task.tag_ids

            if task.description:
                description += "<b>%s</b>:<br/>%s" % (task.name, task.description or 'Sin descripción.')

            if task.work_to_do:
                works += "Trabajo a realizar para el PT <b>%s</b>:<br/>%s" % (task.name, task.work_to_do or 'Sin trabajo a realizar')

        #Creacion tarea
        task_id = self.create({
            'allocated_hours': planned_hours,
            #'date_deadline': deadline_date,
            'project_id': projects.id if projects else False,
            'description': description,
            'work_to_do': works,
            'tag_ids': [(6, 0, tags.ids)] if tags else False,
            'name': ', '.join(current_tasks.mapped('name')),
            'timesheet_ids': [(6, 0, timesheets.ids)] if timesheets else False,
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
    
    def toggle_invoiceable(self):
        res = super(ProjectTask, self).toggle_invoiceable()
        for task in self.merge_task_ids:
            task.toggle_invoiceable()
    
        return res