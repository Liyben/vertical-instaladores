# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Facturación a origen',
    'version': '14.0.1.0.0',
    'category': 'Sales Management',
    'sequence': 6,
    'summary': "Facturación a origen. ",
    'author': 'Liyben Team',
    'company': 'Liyben Team',
    'website': 'http://www.liyben.com',

    'description': """
        Calcula las lineas de facturación previas relacionadas con la misma linea de pedido, para su posterior impresión 
        en el informe de facturación a origen.
    """,
    'depends': ['sale', 'account'],
    'data': [
    ],
    'demo': [
        'views/invoice_report.xml',
        'views/report_invoice_document.xml',
    ],
    'installable': True,
    'auto_install': False,
}