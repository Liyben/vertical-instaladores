# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': "Stock Picking Invoicing SO Journal Type",
    'version': '11.0.1.0.1',
    'category': 'Warehouse Management',
    'author': "Liyben Team",
    'website': 'https://liyben.com',
    'license': 'AGPL-3',
    "depends": [
        "stock_picking_invoicing",
        "sale_order_type",
        "sale_order_type_liyben_modify",
    ],
    "data": [
        "views/sale_order_type_view.xml",
        "wizard/stock_invoice_onshipping_view.xml",
    ],
    "demo": [
    ],
    'installable': True,
}
