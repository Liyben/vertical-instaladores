# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Adaptación Oportunidades para SAT',
    'category': "Customer Relationship Management",
    'summary': 'Se adapta el CRM para el flujo SAT',
    'website': 'https://liyben.com/',
    'version': '17.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Seges',
    'depends': ['sales_team','sale_crm','analytic_plan_on_sale_crm'],
    'data': [
            
        'report/ir_actions_report_crm_templates.xml',
        'report/ir_actions_report.xml',

        'data/lead_sequence.xml',

        'views/crm_lead_views.xml',
        'views/sale_views.xml',
        'views/crm_lead_report.xml',
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
