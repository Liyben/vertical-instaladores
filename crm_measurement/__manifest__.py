# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Productos y secciones para SAT',
    'category': "Customer Relationship Management",
    'summary': 'Permite crear productos con sus secciones para generar un presupuesto con ellos desde un SAT',
    'website': 'https://liyben.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Liyben',
    'depends': ['crm','sale','product','sale_order_line_sections'],
    'data': ['security/ir.model.access.csv',
            'views/crm_lead_views.xml',
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
