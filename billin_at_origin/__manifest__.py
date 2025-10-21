# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Facturación a origen',
    'version': '17.0.1.0.0',
    'summary': """ Facturación a origen """,
    'author': 'Seges',
    'website': 'https://seges.es/',
    'category': '',
    'depends': ['sale', 'account'],
    'data': [
        'report/ir_actions_report_invoice_templates.xml',
        'report/ir_actions_report.xml',
    ],    
    'assets': {
        'web.report_assets_common': [
            'billin_at_origin/static/src/css/report.css',
        ],
        'web.report_assets_pdf': [
            'billin_at_origin/static/src/css/report.css',
        ],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
