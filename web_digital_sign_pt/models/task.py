# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    digital_signature = fields.Binary(string='Firma')
    sign_by = fields.Char(string='Nombre')
    nif = fields.Char(string='DNI')

    @api.model
    def create(self, values):
        task = super(ProjectTask, self).create(values)
        if task.digital_signature:
            values = {'digital_signature': task.digital_signature}
            task._track_signature(values, 'digital_signature')
        return task

    @api.multi
    def write(self, values):
        self._track_signature(values, 'digital_signature')
        return super(ProjectTask, self).write(values)


