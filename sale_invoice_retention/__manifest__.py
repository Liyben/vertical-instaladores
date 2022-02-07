# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Calculo de las retenciones en presupuestos y facturas.',
    'version': '14.0.1.0.0',
    'category': 'Sales Management',
    'sequence': 6,
    'summary': "Calculo de las retenciones en presupuestos y facturas.",
    'author': 'Liyben Team',
    'company': 'Liyben Team',
    'website': 'http://www.liyben.com',

    'description': """
        Calcula la rentención introducida sobre el total del presupuesto o de la factura. 
        Tambien arrastra la retención desde el presupuesto a la factura.
    """,
    'depends': ['sale', 'base', 'account'],
    'data': [
        'views/sale_invoice_retention_view.xml',
        'views/invoice_sale_retention_view.xml',
        'views/report_invoice.xml'
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}