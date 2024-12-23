# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Update apps inf',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Tools',
    'summary': 'Comprobar desde odoo que apps se tienen que actualizar',
    'description': """


    """,
    'author': 'Seges',
    'depends': ['base', 'web'],
    'data': [
        'views/ir_module_views.xml',
        ],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'assets': {
        'web.assets_backend': [
            'web/static/src/legacy/js/apps.js',
        ]
    },
    'css': [
    ],
    'installable': True,
}