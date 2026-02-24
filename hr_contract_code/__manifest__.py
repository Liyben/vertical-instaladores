# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'HR Contract Sequence',
    'version': '17.0.1.0.0',
    'summary': """ Añade una secuencia única a los contratos de empleados para facilitar su identificación y gestión.""",
    'author': 'Seges',
    'website': 'https://www.seges.com',
    'category': 'Human Resources/Contracts',
    'depends': ['hr_contract', ],
    'data': [
        "data/contract_sequence.xml",
        "views/hr_contract_views.xml",
    ],
    
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}
