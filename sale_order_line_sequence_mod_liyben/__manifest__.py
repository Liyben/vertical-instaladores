# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Line Sequence",
    "summary": "Propagates SO line sequence to invoices and stock picking.",
    "version": "11.0.1.0.0",
    "author": "Eficent, "
              "Serpent CS, "
              "Odoo Community Association (OCA)",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow/tree/11.0/sale_order_line_sequence", # noqa
    "license": "AGPL-3",
    'data': ['views/sale_view.xml'],
    "depends": [
        "sale",
    ],
    'post_init_hook': 'post_init_hook',
    "installable": True,
}
