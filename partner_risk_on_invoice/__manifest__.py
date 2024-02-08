# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Limite del seguro en facturas.',
    'version': '14.0.1.0.0',
    'category': 'Accounting',
    'sequence': 6,
    'summary': "Permite agrupar por dos nuevos campos: el límite del seguro del cliente ó por el cliente más el límite de su seguro",
    'author': 'Liyben Team',
    'company': 'Liyben Team',
    'website': 'http://www.liyben.com',

    'description': """
        
    """,
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}