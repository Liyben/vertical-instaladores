# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Trabajos y Materiales en producto',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Trabajos y Materiales en producto',
    'description': """


    """,
    'author': 'Seges',
    'depends': ['sale_crm','project_timesheet_time_control','sale_order_invoicing_finished_task','sale_margin','analytic_plan_on_sale_crm'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'report/ir_actions_report_sale_templates.xml',
        'report/ir_actions_report_invoice_templates.xml',
        'report/ir_actions_report.xml',

        'data/project_data.xml',
        'data/ir_actions_server_data.xml',
        'data/stock_picking_type_data.xml',

        'wizard/sale_order_merge_task_wizard_views.xml',

        'views/product_view.xml',
        'views/sale_view.xml',
        'views/project_task.xml',
        'views/crm_lead_view.xml',
        'views/hr_view.xml',
        'views/account_move_view.xml',
            ],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'assets': {
        'web.report_assets_common': [
            'product_task_material_work/static/src/css/report.css',
        ],
        'web.report_assets_pdf': [
            'product_task_material_work/static/src/css/report.css',
        ],
    },
    'installable': True,
}