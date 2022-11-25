# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Informes de albaran valorado',
    'category': 'Warehouse Management',
    'summary': 'Añade dos nuevos informes a los albaranes. Estos informes están valorado. Módulo basado en stock_picking_report_valued de la OCA.',
    'website': 'https://liyben.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
        """,
    'author': 'Tecnativa, Odoo Community Association (OCA), Liyben',
    'depends': ['stock','sale_stock'],
    'data': [
            'report/report_stockpicking.xml',
            'report/stock_picking_report.xml',
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
