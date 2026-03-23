# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Hide Apps Menu',
    'version': '17.0.1.0.1',
    'summary': """ Oculta el menú de Aplicaciones para todos los usuarios, moviendo el menú al menú Ajustes > Técnico""",
    'author': 'Seges',
    'website': 'https://seges.es',
    'category': 'Tools',
    'depends': ['base', ],
    'data': [
        "views/menu_views.xml",
    ],
    
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
