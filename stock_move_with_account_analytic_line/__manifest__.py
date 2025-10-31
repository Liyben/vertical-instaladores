# © 2025 Sges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Creación de apuntes analiticos desde albaranes',
    'category': "Stock",
    'summary': 'Crea apuntes analiticos para poder controlar los costes / beneficiones de la cuenta analitica sin crear asientos contables.',
    'website': 'https://seges.es/',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['stock_account','stock_picking_analytic'],
    "data": [
        "security/ir.model.access.csv",
        "views/product_category_views.xml",
    ],
    'pre_init_hook': '_pre_init_hook_reset_valuation',
    'post_init_hook': '_post_init_hook_restore_valuation',
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}
