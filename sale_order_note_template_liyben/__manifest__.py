# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Cambio de condiciones y terminos de Text a Html',
    'version': '14.0.1.0.0',
    'category': 'Sales Management',
    'sequence': 6,
    'summary': "Cambia el tipo de campo 'narration' de Text a Html.",
    'author': 'Liyben Team',
    'company': 'Liyben Team',
    'website': 'http://www.liyben.com',

    'description': """
        Cambia el tipo de campo 'narration' de Text a Html
    """,
    'depends': ['account','sale_order_note_template'],
    'data': [
        'views/account_move_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}