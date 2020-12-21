# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Avisos',
    'category': "Customer Relationship Management",
    'summary': 'Añade los avisos',
    'website': 'https://liyben.com/',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['crm','project','sale','sales_team','sale_crm'],
    'data': ['data/crm_stage_data.xml',
            'views/crm_lead_views.xml',
            'views/res_partner_view.xml',
            'views/crm_stage_views.xml',
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
