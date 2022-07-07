# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class StockInvoiceOnshipping(models.TransientModel):
    _inherit = "stock.invoice.onshipping"

    def _action_generate_invoices(self):
        """
        Action to generate invoices based on pickings
        :return: account.move recordset
        """
        pickings = self._load_pickings()
        company = pickings.mapped("company_id")
        if company and company != self.env.company:
            raise UserError(_("All pickings are not related to your company!"))
        pick_list = self._group_pickings(pickings)
        invoices = self.env["account.move"].browse()
        for pickings in pick_list:
            parts = pickings.mapped("move_lines")
            #grouped_moves_list = self._group_moves(moves)
            #parts = self.ungroup_moves(grouped_moves_list)
            for moves_list in parts:
                invoice, invoice_values = self._build_invoice_values_from_pickings(
                    pickings
                )
                lines = [(5, 0, {})]
                line_values = False
                for moves in moves_list:
                    line_values = self._get_invoice_line_values(
                        moves, invoice_values, invoice
                    )
                    if line_values:
                        lines.append((0, 0, line_values))
                if line_values:  # Only create the invoice if it has lines
                    invoice_values["invoice_line_ids"] = lines
                    invoice_values["invoice_date"] = self.invoice_date
                    # this is needed otherwise invoice_line_ids are removed
                    # in _move_autocomplete_invoice_lines_create
                    # and no invoice line is created
                    invoice_values.pop("line_ids")
                    invoice = self._create_invoice(invoice_values)
                    invoice._onchange_invoice_line_ids()
                    invoice._compute_amount()
                    invoices |= invoice
        return invoices