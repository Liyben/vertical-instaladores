# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Añade secuencia para clientes y proveedores',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Base',
    'summary': '',
    'description': """


    """,
    'author': 'Seges',
    'depends': ['base_partner_sequence', 'account'],
    'data': [
            'data/partner_sequence.xml',
            'views/partner_view.xml'
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