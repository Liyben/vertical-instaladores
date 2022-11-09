# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Confirmar pedido en función del producto',
    'category': "Product",
    'summary': 'Restringe la confirmación del pedido en función de los productos de la linea de pedido.',
    'website': 'https://liyben.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['product','sale','merge_pt'],
    'data': ['views/product_views.xml',
            'views/sale_views.xml',
    ],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}
