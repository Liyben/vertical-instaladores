# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _rec_names_search = ["name", "code"]

    code = fields.Char(
        string="Número de contrato",
        required=True,
        default="/",
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        (
            "hr_contract_unique_code",
            "UNIQUE (company_id, code)",
            _("¡El número de contrato debe de ser único!"),
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "/") == "/":
                vals["code"] = (
                    self.env["ir.sequence"].next_by_code("hr.contract") or "/"
                )
        return super().create(vals_list)

    @api.depends('name', 'code')
    def _compute_display_name(self):
        # 1. Llamamos a super() para que calcule el display_name estándar (basado en 'name')
        result = super()._compute_display_name()
        
        # 2. Iteramos para inyectar nuestro código en el display_name
        for rec in self.filtered("code"):
            rec.display_name = f"[{rec.code}] {rec.display_name}"
        
        return result