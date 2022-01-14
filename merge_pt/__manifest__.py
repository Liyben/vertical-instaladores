# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Combinar Partes de Trabajo',
    'category': "Project",
    'summary': 'Combina varios PTs en unp solo',
    'website': 'https://liyben.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['project','project_task_material'],
    'data': [ 'security/ir.model.access.csv',
            'data/project_data.xml', 
            'wizard/project_task_merge_wizard_views.xml'
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