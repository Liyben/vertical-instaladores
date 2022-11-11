# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Unidades producidas',
    'summary': 'Añade las unidades producidas al parte de horas en tareas',
    'website': 'https://liyben.com',
    'author': 'Liyben',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Project',
    'description': """
        """,
    'data': [
        'views/product_views.xml',
        'views/project_task_views.xml',
        'views/account_analytic_view.xml',
    ],
    'depends': ['hr_timesheet', 'uom','product',],
}
