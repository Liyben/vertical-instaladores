# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Geolocalización en Partes de Trabajo',
    'version': '14.0.1.0.0',
    'category': 'Project',
    'summary': """
        Con este módulo la geolocalización del empleado es rastreada en el inicio/fin del parte de trabajo
    """,
    'author': 'Liyben Team',
    'company': 'Liyben Team',
    'website': 'http://www.liyben.com',

    'description': """
        
    """,
    'depends': ['project', 'project_timesheet_time_control', 'account', 'web', 'hr_timesheet'],
    'data': [
        "security/project_task_timer_security.xml",
        "views/assets.xml",
        "views/project_task.xml",
        "views/account_analytic_line_view.xml",
        "data/geolocation_data.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}