# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Trabajos y Materiales en producto',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Trabajos y Materiales en producto',
    'description': """
Este módulo contiene los mecanismos necesarios para manejar un producto como una partida.

En la vista 'sale.report_invoice_layouted' comentar la etiqueta <xpath expr="//table" position="after">...</xpath>
    """,
    'author': 'Liyben',
    'depends': ['sale', 'project_task_material','sale_timesheet','percent_field', 'product',
                'crm_aviso_to_pt','sale_project','account','lyb_avisos_code',
                'project_task_code','sales_team','hr_timesheet','sale_margin',],
    'data': ['data/product_data.xml','views/product_template.xml','views/sale_view.xml','views/hr_view.xml','views/report_saleorder.xml',
            'views/account_invoice_view.xml','views/report_invoice.xml','views/report_stock.xml' , 'views/project_task.xml',
            'security/ir.model.access.csv',],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}