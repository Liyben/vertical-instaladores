# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Facturación desde albaranes adpatada al flujo de Liyben',
    'category': "Stock",
    'summary': '',
    'website': 'https://liyben.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['stock','account','sale','stock_picking_invoicing','purchase_discount'],
    'data': [
            'views/stock_picking.xml',
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
