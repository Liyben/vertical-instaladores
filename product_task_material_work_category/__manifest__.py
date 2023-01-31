# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Trabajos y Materiales en producto en función de la categoria',
    'version': '14.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Trabajos y Materiales en producto',
    'description': """
Este módulo añade la funcionalidad de poder aplicar la tarifa del compuesto, si se define por categoría, a los materiales y mano de obra de dicho compuesto.

    """,
    'author': 'Liyben',
    'depends': ['product_task_material_work'],
    'data': [
            'views/product_template.xml',],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}