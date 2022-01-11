# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'MIS Builder con cuenta analitica en plantillas',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'MIS Builder con cuenta analitica en plantillas',
    'description': """
    MIS Builder con cuenta analitica en plantillas.
    """,
    'author': 'Liyben',
    'depends': ["mis_builder", "account", "sale", "sale_crm", "analytic", "product_task_material_work","l10n_es_mis_report"],
    'data': ["views/mis_report.xml",
            "data/mis_report_balance_liyben.xml",],
    'qweb': [],
    'images': [
    ],
    'demo': [
    ],
    'css': [
    ],
    'installable': True,
}