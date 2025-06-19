# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Fecha creación de pedido de venta',
    'version': '17.0.1.0.1',
    'summary': """ Añade una nueva fecha que contendra la fecha en la que se crea el pedido de venta. Esta fecha si necesitara cambiarla sería posible en estado borrador """,
    'author': 'Seges',
    'website': 'seges.es',
    'category': 'Sales',
    'depends': ['sale', ],
    "data": [
        "views/sale_order_views.xml"
    ],
    
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
