# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Oportunidades a compra',
    'version': '17.0.1.0.0',
    'summary': """ Añade compras a la oportunidad """,
    'description': """
        Este módulo añade la integración entre CRM y Compras:
        - Crear/Ver Pedidos de Compra desde el CRM.
        - Ver el total comprado en la oportunidad.
    """,
    'author': 'Seges',
    'website': 'https://seges.es',
    'category': 'Sales/CRM',
    'depends': ['crm', 'purchase'],
    "data": [
        "views/purchase_order_views.xml",
        "views/crm_lead_views.xml",
    ],
    
    
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
