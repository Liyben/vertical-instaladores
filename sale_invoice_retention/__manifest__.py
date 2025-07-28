# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Sale_invoice_retention',
    'version': '',
    'summary': """ Sale_invoice_retention Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', ],
    "data": [
        "views/account_move_views.xml",
        "views/sale_order_views.xml"
    ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
