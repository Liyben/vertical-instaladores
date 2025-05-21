# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Pie de página personalizado',
    'version': '',
    'summary': """ Pie de página personalizado """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'web'],
    "data": [
        "security/ir.model.access.csv",
        "template/report_tamplate.xml",
        "views/res_company_views.xml",
        "wizards/base_document_layout.xml"
    ],
    
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
