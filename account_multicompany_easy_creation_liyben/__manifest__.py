# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Creación rápida de empresa desde Contabilidad',
    'category': "Accounting",
    'summary': '',
    'website': 'https://liyben.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        Añade un nuevo menú en Facturación / Contabilidad/Configuración/Contabilidad --> Creación sencilla de compañía.
        Añade un nuevo grupo técnico 'Permite la creación rápida de compañia.', para tener acceso a dicho menú y poder crear la nueva compañia.
            
        """,
    'author': 'Liyben',
    'depends': ['account_multicompany_easy_creation',],
    'data': [
        'security/easy_creation_security.xml',
        'security/ir.model.access.csv',
        'views/menuitem.xml',
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
