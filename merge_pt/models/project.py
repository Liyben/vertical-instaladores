# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ProjectTaskMergeWizard(models.TransientModel):
    _inherit = 'project.task.merge.wizard'
    
    #Combina los PTs
    @api.multi
    def merge_tasks(self):
        #Obtenemos los valores para el PT resultante
        values = {
        'user_id': self.user_id.id,
        'description': self.merge_description(),
        'work_to_do': self.merge_work_to_do(),
        'planned_hours': self.merge_planned_hours(),
        'material_ids': self.merge_materials(),
        'timesheet_ids' : self.merge_timesheet(),
        }

        #Creamos un PT nuevo o sobrescribimos uno ya realizado
        if self.create_new_task:
            values.update({
                'name': self.target_task_name,
                'project_id': self.target_project_id.id
                })
            self.target_task_id = self.env['project.task'].create(values)
        else:
            self.target_task_id.write(values)

        #Combina los seguidores de los PTs seleccionados en el PT resultante
        self.merge_followers()

        #Combina los hilos de mensajes de los PTs seleccionados en el PT resultante
        self.target_task_id.message_post_with_view(
            self.env.ref('project.mail_template_task_merge'),
            values={'target': True, 'tasks': self.task_ids - self.target_task_id},
            subtype_id=self.env.ref('mail.mt_comment').id
        )
        (self.task_ids - self.target_task_id).message_post_with_view(
            self.env.ref('project.mail_template_task_merge'),
            values={'target': False, 'task': self.target_task_id},
            subtype_id=self.env.ref('mail.mt_comment').id
        )
        (self.task_ids - self.target_task_id).write({'active': False})

        #Muestra el PT resultante en su vista formulario
        return {
        "type": "ir.actions.act_window",
        "res_model": "project.task",
        "views": [[False, "form"]],
        "res_id": self.target_task_id.id,
        }

    #Combina el trabajo a realiza de los PTs seleccionados
    @api.multi
    def merge_work_to_do(self):
        return '<br/>'.join(self.task_ids.mapped(lambda task: "Trabajo a realizar para el PT <b>%s</b>:<br/>%s" % (task.name, task.work_to_do or 'Sin trabajo a realizar')))

    #Combina las horas estimadas de los PTS seleccionados
    @api.multi
    def merge_planned_hours(self):
        hours = 0
        for task in self.task_ids:
            hours += task.planned_hours
        return hours

    #Combina la lista de materiales de los PTs seleccionados
    @api.multi
    def merge_materials(self):
        material_list = []
        for task in self.task_ids:
            if task.material_ids:
                for material in task.material_ids:
                    material_list.append((0,0, {
                        'product_id' : material.product_id.id,
                        'quantity' : material.quantity
                        }))
        if material_list == []:
            material_list = False

        return material_list

    #Combina los parte de horas de los PTs seleccionados
    @api.multi
    def merge_timesheet(self):
        timesheet_list = []
        for task in self.task_ids:
            if task.timesheet_ids:
                for timesheet in task.timesheet_ids:
                    timesheet_list.append((0,0, {
                        'date' : timesheet.date,
                        'name' : timesheet.name,
                        'employee_id' : timesheet.employee_id.id,
                        'unit_amount' : timesheet.unit_amount,
                        'account_id' : timesheet.account_id.id
                        }))

        if timesheet_list == []:
            timesheet_list = False

        return timesheet_list
