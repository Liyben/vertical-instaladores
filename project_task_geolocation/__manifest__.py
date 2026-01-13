# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Geolocalización en Partes de Trabajo',
    'version': '17.0.1.0.0',
    'category': 'Project',
    'summary': """
        Con este módulo la geolocalización del empleado es rastreada en el inicio/fin del parte de trabajo
    """,
    'author': 'Seges',
    'company': 'Seges',
    'website': 'http://seges.es',

    'description': """
        
    """,
    'depends': [
        'project',
        'hr_timesheet',
        'web',
        'project_timesheet_time_control',
    ],
    "data": [
        "views/account_analytic_line_view.xml",
        "views/project_task_views.xml",
        "views/project_project_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'project_task_geolocation/static/src/xml/*.xml',
            'project_task_geolocation/static/src/js/*.js',
        ],
    },

    'installable': True,
    'license': 'AGPL-3',
    'auto_install': False,
}