# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class ProjectTask(models.Model):
    _inherit = 'project.task'
    _rec_names_search = ["name", "code"]

    code = fields.Char(
        string="Número de tarea",
        required=True,
        default="/",
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        (
            "project_task_unique_code",
            "UNIQUE (company_id, code)",
            _("¡El número debe de ser único!"),
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "/") == "/":
                vals["code"] = (
                    self.env["ir.sequence"].next_by_code("project.task") or "/"
                )
        return super().create(vals_list)

    def name_get(self):
        result = super().name_get()
        new_result = []

        for task in result:
            rec = self.browse(task[0])
            name = "[{}] {}".format(rec.code, task[1])
            new_result.append((rec.id, name))
        return new_result