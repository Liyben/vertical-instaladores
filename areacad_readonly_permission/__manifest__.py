# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Permiso de solo lectura para algunos usuarios',
    'summary': 'Define que usuarios pueden editar ciertos campos en los diferentes modelos',
    'category': 'Project Management',
    'website': 'https://liyben.com/',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['project', 'hr_timesheet','project_task_geolocation'],
    'data': ['security/areacad_readonly_permission_security.xml','views/hr_timesheet_view.xml',],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}
