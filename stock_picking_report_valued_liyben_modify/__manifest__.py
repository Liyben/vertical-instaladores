# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Modificación al report de albaran',
    'category': "Stock",
    'summary': 'Cambios al report del módulo stock_picking_report_valued',
    'website': 'https://liyben.com/',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
            Este módulo hace cambios al report del módulo stock_picking_report_valued.
        """,
    'author': 'Liyben',
    'depends': ['stock_picking_report_valued','stock','purchase'],
    'data': [
        'report/report_stock.xml',
        'views/stock_move_line_view.xml'
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
