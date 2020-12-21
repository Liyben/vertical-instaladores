# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    #Campos para adpatar el formulario a PT
    ask_by = fields.Char(string='Solicitado por')
    #brand = fields.Char(string='Marca')
    #model_unit_int = fields.Char(string='Modelo Int')
    #model_unit_ext = fields.Char(string='Modelo Ext')
    #serial_number_int = fields.Char(string='Serie MI')
    #serial_number_ext = fields.Char(string='Serie ME')

    work_to_do = fields.Html(string='Trabajo a realizar')
    work_done = fields.Html(string='Trabajo realizado')

    move = fields.Boolean(string='Desplazamiento?', default=False)

    #Hacen visibles los campos de texto
    visible_work_to_do = fields.Boolean(string='Ver campo?', default=False)
    visible_work_done = fields.Boolean(string='Ver campo?', default=False)


    #Función para imprimir el report
    @api.multi
    def print_pt(self):
        return self.env.ref('report_parte_trabajo.report_parte_trabajo_action').report_action(self)
