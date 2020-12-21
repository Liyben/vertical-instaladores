# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Cliente y albaran en movimiento de producto',
    'category': "Stock",
    'summary': 'Muestra el cliente y albaran relacionado en el movimiento de producto',
    'website': 'https://liyben.com/',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
            Muestra el cliente y albaran relacionado en el movimiento de producto.
        """,
    'author': 'Liyben',
    'depends': ['base','stock'],
    'data': [
        'views/stock_view.xml',
        
    ],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}
