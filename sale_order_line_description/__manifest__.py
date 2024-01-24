# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Descripción de la linea de presupuesto',
    'version': '14.0.0.0',
    'summary': 'La descripcion de la linea de presupuesto toma como valor el nombre + descripción de venta del producto',
    'category':'Sale',
    'author': 'Liyben',
    'website': 'liyben.com',
    'description':"""La descripcion de la linea de presupuesto toma como valor el nombre + descripción de venta del producto""", 
    'depends':['sale'],
    'data':[
        'security/sale_order_line_security.xml',
        'views/res_config_settings_views.xml',
        ],
    'installable': True,
    'auto_install': False,
    "images":[],
}


