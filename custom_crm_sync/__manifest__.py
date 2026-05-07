# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Custom CRM Sync',
    'version': '17.0.1.0.0',
    'summary': """ Modifica la sincronización de campos entre Cliente y Oportunidad """,
    'description': 'Fuerza la carga de datos del cliente (incluso vacíos) en el Lead y rompe la sincronización inversa hacia la ficha del cliente.',
    'author': 'Seges',
    'website': 'https://seges.es',
    'category': 'Sales/CRM',
    'depends': ['crm', ],
    'data': [
        
    ],
    
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
