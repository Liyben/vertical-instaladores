# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Crear Tarea desde Oportunidad/Iniciativa',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Crear Tarea desde Oportunidad/Iniciativa. Basado en el modulo crm_lead_to_task de OCA',
    'description': """


    """,
    'author': 'Seges',
    'depends': ['product_task_material_work'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/crm_lead_convert2task_views.xml',
        'views/crm_lead_views.xml'
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