# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class ProjectTaskWork(models.Model):
    """Modelo para almacenar los trabajos de la linea de pedido en el parte de trabajo"""

    _name = 'project.task.work'
    _description = 'Trabajos en el parte de trabajo'
    _order = 'project_task_id, sequence, id'

    #Campo relación con el parte de trabajo
    project_task_id = fields.Many2one(comodel_name='project.task', string='Parte de trabajo', ondelete='cascade')
    #Mano de obra
    work_id = fields.Many2one(comodel_name='product.product', string='Mano de obra', required=True)
    #Descripcion del trabajo
    name = fields.Char(string='Nombre', required=True)
    #Horas empleadas en el trabajo
    hours = fields.Float(string='Horas')
    #Secuencia
    sequence = fields.Integer()
    #Indica si esta realizado por el tecnico
    to_done = fields.Boolean(string='Realizado', default=False)
    #Indica si esta validado
    validated = fields.Boolean(string='Validado', default=False)

    #Carga el nombre de la mano de obra
    @api.onchange('work_id')
    def _onchange_work_id(self):
        for record in self:
            record.name = record.work_id.name

