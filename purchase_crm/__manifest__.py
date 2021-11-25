# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Oportunidades a compra',
    'summary': 'Añade compras a la oportunidad',
    'website': 'https://liyben.com',
    'author': 'Liyben',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'CRM',
    'description': """
        """,
    'data': [
        'views/purchase_order_views.xml',
        'views/crm_lead_views.xml',       
    ],
    'depends': ['crm','purchase'],
}
