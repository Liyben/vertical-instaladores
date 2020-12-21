# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    #Campo para relacionar Aviso con PT
    task_ids = fields.One2many(
        comodel_name='project.task',
        inverse_name='oppor_id',
        string="Partes de Trabajo",
    )

    #Campo contador de los PTs relacionados con el Aviso
    task_number = fields.Integer(compute='_compute_task_total', string="Número de PT")

    project_id = fields.Many2one('project.project', string='Proyecto')

    #Campo para saber si el campo Proyecto es solo lectura o no
    project_only_read = fields.Boolean(string='Solo lectura', compute='_compute_project_only_read')

    #Define el valor para poner el campo project como solo lectura
    @api.multi
    @api.depends('task_ids','order_ids')
    def _compute_project_only_read(self):
        for record in self:
            if (record.task_ids or record.order_ids):
                record.project_only_read = True
            else:
                if (not record.task_ids and not record.order_ids):
                    record.project_only_read = False

    #Lanzamos una excepcion si el aviso tiene ya algun presupuesto o parte de trabajo
    @api.multi
    @api.onchange('project_id')
    def _onchange_project_id(self):
        for record in self:
            if record.project_only_read:
                raise ValidationError(_('No puede crear/modificar el proyecto relacionado con '
                    'un aviso que contenga algun presupuesto o PT.'))


    #Calculo del numero de PTs
    @api.depends('task_ids')
    def _compute_task_total(self):
    	for oppor in self:
    		nbr = 0
    		for task in oppor.task_ids:
    			nbr += 1
    		oppor.task_number = nbr