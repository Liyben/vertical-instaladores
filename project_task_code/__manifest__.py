# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Número serie en tareas',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Project',
    'summary': 'Número serie en tareas',
    'description': """


    """,
    'author': 'Seges',
    'depends': ['project'],
    'data': [
        'data/task_sequence.xml',
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
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}