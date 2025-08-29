# © 2025 Sges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Version de Odoo en barra de menu',
    'version': '17.0.1.0.0',
    'summary': """ Version de Odoo en barra de menu """,
    'author': 'Seges',
    'website': 'https://seges.es/',
    'category': 'Tools',
    'depends': ['base', 'web'],
    'data': [
        
    ],
    'assets': {
              'web.assets_backend': [
                  'systray_odoo_version/static/src/js/*.js',
                  'systray_odoo_version/static/src/xml/*.xml',
              ],
          },
    
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
