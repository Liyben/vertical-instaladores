# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Plan analítico en Pedido y Crm',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Plan analítico en Pedido y Crm',
    'description': """


    """,
    'author': 'Seges',
    'depends': ['sale_project', 'crm_timesheet'],
    "data": [
        "views/crm_lead_views.xml",
        "views/crm_team_views.xml",
        "views/sale_view.xml"
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