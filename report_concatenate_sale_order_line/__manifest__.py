# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Concatena la descripción del compuesto con sus materiales',
    'category': "Sale",
    'summary': 'Concatena la descripción del compuesto con sus materiales seleccionados en su ficha de producto',
    'website': 'https://liyben.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['product','product_task_material_work',],
    'data': ['views/product_views.xml',
            'views/report_saleorder.xml',
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
