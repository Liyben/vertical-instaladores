# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Por Administración desde la Tarea',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Por Administración desde la Tarea',
    'description': """


    """,
    'author': 'Seges',
    'depends': ['product_task_material_work', 'project_task_code'],
    'external_dependencies': {"python": ['html2text']},
    'data': [
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