# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Crear Presupuesto desde la Tarea',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Crear Presupuesto desde la Tarea',
    'description': """


    """,
    'author': 'Seges',
    'depends': ['product_task_material_work'],
    'external_dependencies': {"python": ['html2text']},
    'data': [
        'security/ir.model.access.csv',
        'wizard/project_task_convert2order_views.xml',
        'views/project_task.xml',
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