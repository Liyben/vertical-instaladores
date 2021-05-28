# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CrmOpporConvert2Task(models.TransientModel):
    """ wizard to convert a Lead into a Project task and move the Mail Thread """

    _name = "crm.oppor.convert2task"
    _inherit = 'crm.partner.binding'

    @api.model
    def default_get(self, fields):
        result = super(CrmOpporConvert2Task, self).default_get(fields)
        oppor_id = self.env.context.get('active_id')
        if oppor_id:
            result['oppor_id'] = oppor_id
        return result

    oppor_id = fields.Many2one('crm.lead', string='Aviso', domain=[('type', '=', 'opportunity')])
    project_id = fields.Many2one('project.project', string='Proyecto')
    #Campo para saber si el campo Proyecto es solo lectura o no
    project_only_read = fields.Boolean(string='Solo lectura')


    # Cambiamos el proyecto en el aviso si lo cambiamos en el wizard
    @api.multi
    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.ensure_one()
        # Obtenemos el aviso que vamos a transformar
        oppor = self.oppor_id
        if oppor:
            oppor.project_id = self.project_id.id

    @api.multi
    def action_opportunity_to_project_task(self):
        self.ensure_one()
        # Obtenemos el aviso que vamos a transformar
        oppor = self.oppor_id
        partner_id = self._find_matching_partner()
        if not partner_id and (oppor.partner_name or oppor.contact_name):
            partner_id = oppor.handle_partner_assignation()[oppor.id]
        # Creamos una nueva project.task
        vals = {
            "name": oppor.name,
            "work_to_do": oppor.description,
            "email_from": oppor.email_from,
            "project_id": self.project_id.id,
            "partner_id": partner_id,
            "user_id": oppor.worker_one.id,
            "oppor_id": oppor.id
        }
        task = self.env['project.task'].create(vals)
        # Comentamos el traspaso del hilo y de los ajuntos
        """
        #  Movemos el hilo del mail
        oppor.message_change_thread(task)
        # Movemos los adjuntos
        attachments = self.env['ir.attachment'].search([('res_model', '=', 'crm.lead'), ('res_id', '=', oppor.id)])
        attachments.write({'res_model': 'project.task', 'res_id': task.id})
        """
        # devolvemos la acción para ir a la vista formulario de la nueva tarea
        view = self.env.ref('project.view_task_form2')
        return {
            'name': 'Task created',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'res_id': task.id,
            'context': self.env.context
        }
