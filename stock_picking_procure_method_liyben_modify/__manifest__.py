# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Picking Procure Method Modify Liben',
    'summary': 'Adapta el modulo stock_picking_procure_method a nuestro flujo',
    'website': 'https://liyben.com/',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
            Este módulo adapta el modulo stock_picking_procure_method a nuestro flujo
        """,
    'author': 'Liyben',
    'depends': [
        'stock', 'stock_picking_procure_method',
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    'installable': True,
}
