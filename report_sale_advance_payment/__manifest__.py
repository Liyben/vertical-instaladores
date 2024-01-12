# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Report pagos anticipados',
    'category': "Sale",
    'summary': "Se añade a la impresiópn del informe de presupuestos los pagos anticipados si este los tuviera",
    'website': 'https://liyben.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['sale','sale_advance_payment',],
    'data': [
            'views/reportsaleorder.xml',
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
