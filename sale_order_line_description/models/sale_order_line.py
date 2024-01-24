# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if not self.product_id:  # pragma: no cover
            return res
        if (
            self.user_has_groups(
                "sale_order_line_description."
                "group_use_product_name_and_description_per_so_line"
            )
        ):
            product = self.product_id
            if self.order_id.partner_id:
                product = product.with_context(
                    lang=self.order_id.partner_id.lang,
                )
            self.name = product.name + ". " + product.description_sale
        return res