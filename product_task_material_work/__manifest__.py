# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Trabajos y Materiales en producto',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Trabajos y Materiales en producto',
    'description': """
Este módulo contiene los mecanismos necesarios para manejar un producto como una partida. Tambien añade la impresión de facturas agrupadas por albaran
basada en el módulo de la OCA 'account_invoice_report_grouped_by_picking'.

    """,
    'author': 'Liyben',
    'depends': ['sale_project','sale_crm','project_timesheet_time_control','sale_order_invoicing_finished_task'],
    'data': [
        'data/project_data.xml',
        'data/ir_actions_server_data.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/product_view.xml',
        'views/sale_view.xml',
        'views/project_task.xml',
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