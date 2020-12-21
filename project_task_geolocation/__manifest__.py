# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Geolocalización en Partes de Trabajo',
    'summary': """
        Con este módulo la geolocalización del empleado es rastreada en el inicio/fin
    """,
    'website': 'https://liyben.com',
    'author': 'Liyben',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Project',
    'description': """

        """,
    'depends': ['project', 'hr_timesheet','decimal_precision','merge_pt'],
    'data': [
        'views/project_task_geolocation_view.xml',
        'views/project_geolocation_static.xml',
        'data/geolocation_data.xml',
    ],
}
