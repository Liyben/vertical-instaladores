# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Firma Web Digital en albaranes',
    'category': "Project",
    'summary': 'Habilitar la pantalla táctil para que el usuario pueda agregar firmas con dispositivos táctiles en los albaranes.',
    'website': 'https://liyben.com/',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
            Este módulo proporciona la funcionalidad para almacenar firma digital en los albaranes.
        """,
    'author': 'Liyben',
    'depends': ['web_widget_digitized_signature','stock'],
    'data': [
        'views/stock_view.xml',
        'report/report_stock.xml'
        
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
