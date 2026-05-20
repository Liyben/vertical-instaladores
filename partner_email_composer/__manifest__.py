# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Partner Email Composer Recipients',
    'version': '17.0.1.0.0',
    'summary': 'Añade contactos hijos automáticamente al enviar presupuestos y facturas.',
    'description': """
        Intercepta la carga del wizard estándar de correos (mail.compose.message) 
        y el wizard de envío de facturas (account.move.send) en Odoo 17 para inyectar 
        automáticamente a los contactos hijos que tengan la opción marcada.
    """,
    'author': 'Seges',
    'website': 'https://www.seges.es',
    'category': 'Productivity/Discuss',
    'depends': [
        'contacts',
        'mail',
        'sale',
        'account',
    ],
    "data": [
        "views/res_partner_views.xml"
    ],
    
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
