# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Report para los presupuestos',
    'category': "Sale",
    'summary': 'Impresión de los presupuestos sin precios',
    'website': 'https://liyben.com/',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['sale', 'base_report_liyben_aviso', 'product_task_material_work'],
    'data': ['views/report_saleorder.xml',
    ],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}
