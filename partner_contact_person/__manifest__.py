# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Persona de contacto y móvil",
    "category": "Extra Tools",
    "summary": "Añade una persona de contacto indicando su móvil, en la ficha de cliente llevando dicha información al aviso",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Liyben",
    "website": "",
    "depends": ["base_setup", "lyb_avisos"],
    "data": ["views/res_partner.xml",
            "views/crm_lead.xml",
            'views/report_crm_lead_document.xml',],
    "installable": True,
}
