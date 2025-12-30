# -*- coding: utf-8 -*-
{
    'name': 'Sale_order_line_layout',
    'version': '17.0.1.0.0',
    'summary': """ Sale_order_line_layout Summary """,
    'author': 'Seges',
    'website': 'https://seges.es/',
    'category': 'Sale',
    'depends': ['sale', 'sale_margin',],
    'data': [
        "security/ir.model.access.csv",
        'security/sale_order_line_layout_groups_groups.xml'
        "views/sale_order_line_layout_views.xml",
    ],
    
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
