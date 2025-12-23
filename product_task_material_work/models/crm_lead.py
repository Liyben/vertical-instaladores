# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    #Campo para relacionar Aviso / Oportunidad con PT
    task_ids = fields.One2many(comodel_name='project.task', inverse_name='oppor_id', string="Partes de Trabajo")

    task_number = fields.Integer(
        string="Número de PT",
        compute='_compute_task_total',
        store=True,  
        readonly=True
    )

    @api.depends('task_ids')
    def _compute_task_total(self):
        for record in self:
            record.task_number = len(record.task_ids)
    
    