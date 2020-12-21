# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Cuenta analítica madre en pedido/presupuesto de venta',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Cuenta analítica madre en pedido/presupuesto de venta',
    'description': """
Este módulo contiene los mecanismos necesarios para manejar una cuenta analítica madre desde el aviso hasta el proyecto.
    """,
    'author': 'Liyben',
    'depends': ['sale', 'lyb_avisos', 'crm_aviso_to_pt','sale_crm','account_analytic_parent'],
    'data': ['views/sale_views.xml','views/account_analytic_account_view.xml','views/crm_lead_views.xml','data/analytic_account.xml'],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}