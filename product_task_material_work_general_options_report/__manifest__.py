# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Opciones de impresion en presupuestos',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Trabajos y Materiales en producto',
    'description': """
Este módulo generaliza las opciones de impresión del módulo Trabajos y Materiales en producto,
es decir añade la posibilidad de activar las distintas opciones de impresión de todas las líneas de 
presupuestos desde el presupuesto.
    """,
    'author': 'Liyben',
    'depends': ['product_task_material_work'],
    'data': ['views/sale_view.xml',],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}