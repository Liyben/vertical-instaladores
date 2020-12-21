# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Report para los avisos',
    'category': "Customer Relationship Management",
    'summary': 'Impresión de los avisos.',
    'website': 'https://liyben.com/',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['crm','project','base_report_liyben_aviso','lyb_avisos'],
    'data': ['views/aviso_report.xml',
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
