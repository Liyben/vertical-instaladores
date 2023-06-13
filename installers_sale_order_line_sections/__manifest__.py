# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "Calculo de secciones (VERTICAL)",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Secciones en linea de pedido',
    'description': """
Este módulo contiene los mecanismos necesarios para manejar las secciones dentro de la linea de pedido.
    """,
    'author': 'Liyben',
    'depends': ['sale', 'uom', 'product_task_material_work'],
    'data': ['views/sale_view.xml',
            'data/uom_data.xml',
            'security/ir.model.access.csv',
            'views/report_saleorder.xml',],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}