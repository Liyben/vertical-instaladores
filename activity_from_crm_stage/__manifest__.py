# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Actividades en etapas',
    'category': "Customer Relationship Management",
    'summary': 'Asigna un tipo de actividad a la etapa. Cuando el aviso o la oportunidad pasa a dicha etapa creara la actividad asociada.',
    'website': 'https://liyben.com/',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'description': """
        
            
        """,
    'author': 'Liyben',
    'depends': ['mail','crm'],
    'data': [
        'views/crm_stage_view.xml',
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
