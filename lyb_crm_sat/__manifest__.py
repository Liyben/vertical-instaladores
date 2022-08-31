# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Adaptación Oportunidades para SAT',
    'category': "Customer Relationship Management",
    'summary': 'Se adapta el CRM para el flujo SAT',
    'website': 'https://liyben.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['crm','project','sale','sales_team','sale_crm','crm_timesheet'],
    'data': ['data/lead_sequence.xml',
            'views/crm_lead_views.xml',
            'views/crm_lead_report.xml',
            'views/report_crm_lead_document.xml',
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
