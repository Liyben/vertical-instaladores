# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Número de albaran de proveedor',
    'category': "Stock",
    'summary': '',
    'website': 'https://liyben.com/',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
            Este módulo muestra el número de albarán de proveedor.
        """,
    'author': 'Liyben',
    'depends': ['base','stock'],
    'data': [
        'views/stock_view.xml',
        'report/report_stock.xml'
        
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
