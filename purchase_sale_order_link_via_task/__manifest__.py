# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Order - Sale Order Link via Task",
    "summary": "Muestra los Pedidos de Venta asociados a un Pedido de Compra a través de las Tareas del Proyecto.",
    "description": """
        Este módulo añade un Smart Button en los Pedidos de Compra para acceder a los Pedidos de Venta vinculados.
        
        La relación se realiza buscando Tareas (project.task) que tengan asignado el mismo Grupo de Abastecimiento que el Pedido de Compra actual, y leyendo su elemento de pedido de venta asociado.
        
        NOTA DE CONFIGURACIÓN IMPORTANTE:
        Para que este módulo funcione correctamente, se debe configurar la propagación del grupo de abastecimiento en la Regla de Compra (Buy Route). El campo 'Propagar Grupo de Abastecimiento' debe estar configurado como 'Propagar', para que las compras adquieran el mismo Procurement Group asociado a las tareas que generan los albaranes.
    """,
    "version": "17.0.1.0.0",
    "category": "Inventory/Purchase",
    "author": "Seges-SL",
    "website": "https://github.com/Seges-SL",
    "depends": [
        "purchase_stock",
        "project_stock",
        "sale_project",
    ],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
