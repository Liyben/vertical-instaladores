# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Retención en ventas y facturas',
    'version': '17.0.1.0.0',
    'summary': """ Retención en ventas y facturas """,
    'author': 'Seges',
    'website': 'seges.es',
    'category': 'Sales',
    'depends': ['sale', 'account' ],
    "data": [
        "data/decimal_precision_data.xml",
        "views/report_invoice.xml",
        "views/account_move_views.xml",
        "views/sale_order_views.xml"
    ],
    
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
