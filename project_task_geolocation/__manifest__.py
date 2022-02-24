# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Geolocalización en Partes de Trabajo',
    'version': '14.0.1.0.0',
    'category': 'Project',
    'sequence': 6,
    'summary': """
        Con este módulo la geolocalización del empleado es rastreada en el inicio/fin
    """,
    'author': 'Liyben Team',
    'company': 'Liyben Team',
    'website': 'http://www.liyben.com',

    'description': """
        
    """,
    'depends': ['project', 'project_timesheet_time_control', 'account', 'web'],
    'data': [
        "views/assets.xml",
        "data/geolocation_data.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}