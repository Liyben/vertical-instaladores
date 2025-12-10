# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Link a los pedidos de compra desde albarán',
    'version': '17.0.1.0.1',
    'summary': """ Link de los pedidos de compra que tengan el mismo grupo de abestecimiento que el albarán """,
    'author': 'Seges',
    'website': 'https://seges.es',
    'category': 'Stock',
    'depends': ['purchase_stock', ],
    "data": [
        "views/stock_picking_views.xml"
    ],
    
    
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
