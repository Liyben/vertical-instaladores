# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Sale Line Description to Stock Move',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Delivery',
    'summary': 'Propaga la descripción personalizada de la línea de presupuesto al albarán de entrega.',
    'description': """
        Este módulo intercepta el flujo de abastecimiento (procurement) para asegurar
        que la descripción introducida manualmente en la línea de venta viaje hasta
        el movimiento de stock (stock.move) y, por ende, sea visible en el albarán.
    """,
    'author': 'Seges',
    'website': 'https://seges.es',
    'depends': ['sale_stock', ],
    'data': [
        
    ],
    
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
