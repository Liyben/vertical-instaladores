# © 2019 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "author": "Liyben",
    "name": "Añadir número de código para avisos",
    "version": "11.0.1.0.0",
    "category": "Customer Relationship Management",
    "website": "https://liyben.com",
    "depends": [
        'crm',
        'lyb_avisos',
    ],
    "summary": "Establece el número de código para avisos desde una secuencia",
    "data": [
        "views/crm_lead_view.xml",
        "data/lead_sequence.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
