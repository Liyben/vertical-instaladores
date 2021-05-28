# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Combinación automática de PT´s',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Combinanción automática de partes de trabajos al confirmar un pedido de venta',
    'description': """
Este módulo contiene los mecanismos necesarios para combinar los partes de trabajos resultantes de confirmar un presupuesto de venta, 
si los hubiera, en un solo.
    """,
    'author': 'Liyben',
    'depends': ['product_task_material_work', 'project','sale_timesheet',],
    'data': [],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}