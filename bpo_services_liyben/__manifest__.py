# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Servicios BPO',
    'category': "Project",
    'summary': 'Añade los servicios BPO',
    'website': '',
    'version': '11.0.2.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['project'],
    'data': ['views/bpo_views.xml',
        'security/bpo_service_security.xml',
        'security/ir.model.access.csv',
        'data/bpo_service_data.xml',
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
