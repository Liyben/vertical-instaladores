# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    custom_report_footer = fields.Html(related='company_id.custom_report_footer', readonly=False,)

    @api.depends(
        "custom_report_footer",
    )
    def _compute_preview(self):
        return super()._compute_preview()