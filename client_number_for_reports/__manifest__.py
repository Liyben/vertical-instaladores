# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Número de cliente en presupuestos, facturas y albaranes',
    'version': '14.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Número de cliente en presupuestos, facturas y albaranes',
    'description': """
Número de cliente en presupuestos, facturas y albaranes

    """,
    'author': 'Liyben',
    'depends': ['sale', 'account', 'stock'],
    'data': [
            'views/sale_view.xml',
            'views/account_move_view.xml',
            'views/stock_picking_view.xml',
            'views/report_saleorder.xml',
            'views/report_stock.xml',
            'views/report_invoice.xml',],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}