# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Trabajos y Materiales en producto',
    'version': '14.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Trabajos y Materiales en producto',
    'description': """
Este módulo contiene los mecanismos necesarios para manejar un producto como una partida.

    """,
    'author': 'Liyben',
    'depends': ['sale', 'project_task_material','sale_timesheet', 'product',
                'sale_project','account', 'project_task_code','sales_team','hr',
                'hr_timesheet','sale_margin','crm','uom'],
    'data': ['data/product_data.xml',
            'views/product_template.xml',
            'views/sale_view.xml',
            'views/hr_view.xml',
            'views/account_move_view.xml',
            'views/project_task.xml',
            'views/crm_lead_view.xml',
            'security/ir.model.access.csv',
            'security/account_move_security.xml',
            'security/sale_security.xml',
            'views/sale_report.xml',
            'views/project_task_report.xml',
            'views/report_saleorder.xml',
            'views/report_projecttask.xml',
            'views/report_invoice.xml',],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}