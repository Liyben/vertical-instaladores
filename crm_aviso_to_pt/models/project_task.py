# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    oppor_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Aviso',
    )