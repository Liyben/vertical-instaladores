# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_order_count_from_tasks = fields.Integer(
        compute="_compute_sale_order_count_from_tasks",
        string="Nº Pedidos de Venta",
    )

    @api.depends("group_id")
    def _compute_sale_order_count_from_tasks(self):
        for order in self:
            count = 0
            if order.group_id:
                # Obtenemos las tareas asociadas al grupo de abastecimiento
                tasks = self.env["project.task"].search([
                    ("group_id", "=", order.group_id.id)
                ])
                if tasks:
                    # Extraemos los SOs únicos y los contamos directamente
                    sales = tasks.mapped("sale_line_id.order_id") | tasks.mapped("sale_order_id")
                    count = len(sales)
            order.sale_order_count_from_tasks = count

    def action_view_sale_orders_from_tasks(self):
        """
        Calcula el dominio dinámicamente y abre la vista de ventas.
        Se restringe la creación manual para mantener la integridad del flujo.
        """
        self.ensure_one()
        
        # Localizamos los registros para el dominio con el campo correcto
        tasks = self.env["project.task"].search([
            ("group_id", "=", self.group_id.id)
        ])
        sales = tasks.mapped("sale_line_id.order_id") | tasks.mapped("sale_order_id")
        
        # Definimos el contexto desactivando la creación ('create': False)
        action_context = {
            **self.env.context,
            'default_company_id': self.company_id.id,
            'create': False,
        }

        action = {
            "name": "_(Pedidos de Venta Asociados)",
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "context": action_context,
            "domain": [("id", "in", sales.ids)],
        }
        
        # Redirección a formulario si solo hay un resultado
        if len(sales) == 1:
            action.update({
                "view_mode": "form",
                "res_id": sales.id,
                "views": [(self.env.ref("sale.view_order_form").id, "form")],
            })
        else:
            action["view_mode"] = "tree,form"
            
        return action
