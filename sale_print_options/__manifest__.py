# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Opciones de impresión para presupuestos',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': '',
    'description': """


    """,
    'author': 'Seges',
    'depends': ['product_task_material_work'],
    'data': [
            'security/security.xml',
            'report/ir_actions_report_invoice_templates.xml',
            'report/ir_actions_report_sale_templates.xml',
            'views/product_views.xml',
            'views/sale_view.xml'
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