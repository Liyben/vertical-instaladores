# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def button_project_task_to_crm_lead(self):
        self.ensure_one()

        # Creamos un nuevo aviso
        vals = {
            "name": '[' + self.code + ']: ' + self.name,
            "note": self.work_to_do,
            "email_from": self.email_from,
            "project_id": self.project_id.id,
            "partner_id": self.partner_id.id,
            "user_id": self._uid,
            "type": 'opportunity',
            "sub_type" : 'notice',
            "partner_name": self.partner_id.name or ''
        }
        aviso = self.env['crm.lead'].create(vals)

        # Asociamos el aviso a la tarea
        self.oppor_id = aviso.id
        
        # devolvemos la acción para ir a la vista formulario del nuevo aviso
        view = self.env.ref('crm.crm_lead_view_form')
        return {
            'name': 'Aviso creado',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'res_id': aviso.id,
            'context': self.env.context
        }

