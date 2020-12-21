# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock desde Parte de Trabajos',
    'summary': """
        Con este módulo podrá consultar los alabaranes asociados a su parte de trabajo
    """,
    'website': 'https://liyben.com',
    'author': 'Liyben',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Project',
    'description': """

        """,
    'depends': ['project', 'stock_account','project_task_code','project_task_material','project_task_material_stock','product_task_material_work','stock_analytic'],
    'data': [
        'views/project_task_views.xml',
    ],
}
