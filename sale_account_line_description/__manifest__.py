# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Custom Line Descriptions (Sale & Invoice)',
    'version': '17.0.1.0.0',
    'summary': """ Aplica reglas personalizadas a la descripción de líneas en presupuestos y facturas de venta. """,
    'description': """
        Reglas aplicadas en account.move.line y sale.order.line:
        1. Producto vacío -> Nombre vacío.
        2. Producto con descripción de venta -> Nombre = Descripción de venta.
        3. Producto sin descripción de venta -> Nombre = Nombre del producto.
    """,
    'author': 'Seges',
    'website': 'https://seges.es',
    'category': 'Sales Management',
    'depends': ['sale', 'account'],
    'data': [
        
    ],
    
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
