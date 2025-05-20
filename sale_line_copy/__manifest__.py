# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Copia de la linea de presupuesto',
    'version': '17.1.0.0',
    'summary': 'Duplica la linea de presupuesto',
    'category':'Sale',
    'author': 'Seges',
    'website': 'seges.es',
    'description':"""Duplica la linea de presupuesto""", 
    'depends':['sale'],
    'data':[
        'security/sale_order_line_copy_group.xml',
        'views/sale_order_line_view.xml',
        ],
    'installable': True,
    'auto_install': False,
    "images":[],
}


