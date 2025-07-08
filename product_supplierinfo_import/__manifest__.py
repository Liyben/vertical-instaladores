# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'Actualizar tarifas de proveedor',
    'version': '17.0.1.0.0',
    'summary': """ Actualizar tarifas de proveedor """,
    'author': 'Seges',
    'website': 'seges.es',
    'category': 'Product',
    'depends': ['purchase_triple_discount', 'product', 'purchase' ],
    "data": [
        "data/decimal_precision_data.xml",
        "security/ir.model.access.csv",
        "security/product_supplierinfo_import_security.xml",
        "views/product_supplierinfo_views.xml",
        "wizards/import_product_supplierinfo.xml"
    ],
    
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
