# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Avisos a Parte de Trabajo',
    'summary': 'Crear Partes de Trabajo desde Avisos',
    'website': 'https://liyben.com',
    'author': 'Liyben',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Project',
    'description': """
Avisos a Parte de Trabajo
=========================

Asocia y crea los partes de trabajo a partir de los avisos.
        """,
    'data': [
        'security/ir.model.access.csv',
        'wizard/crm_opportunity_convert2task_views.xml',
        'views/crm_opportunity_views.xml',
        'views/project_task_view.xml',
    ],
    'depends': ['crm', 'project','sale_crm','task_mode_pt', 'lyb_avisos','project_task_code'],
}
