# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # ---------------------------------------------------------
    # 1. SOBRESCRIBIR MÉTODOS COMPUTE
    # Al eliminar la condición "if lead.partner_id.email:" nativa, 
    # forzamos a que siempre se copie el valor de la ficha del cliente, 
    # incluso si es False (vacío), sobreescribiendo el dato de la oportunidad.
    # ---------------------------------------------------------

    @api.depends('partner_id')
    def _compute_email_from(self):
        for lead in self:
            if lead.partner_id:
                lead.email_from = lead.partner_id.email

    @api.depends('partner_id')
    def _compute_phone(self):
        for lead in self:
            if lead.partner_id:
                lead.phone = lead.partner_id.phone

    @api.depends('partner_id')
    def _compute_mobile(self):
        for lead in self:
            if lead.partner_id:
                lead.mobile = lead.partner_id.mobile

    @api.depends('partner_id')
    def _compute_website(self):
        for lead in self:
            if lead.partner_id:
                lead.website = lead.partner_id.website

    @api.depends('partner_id')
    def _compute_function(self):
        for lead in self:
            if lead.partner_id:
                lead.function = lead.partner_id.function

    @api.depends('partner_id')
    def _compute_title(self):
        for lead in self:
            if lead.partner_id:
                lead.title = lead.partner_id.title

    @api.depends('partner_id')
    def _compute_contact_name(self):
        for lead in self:
            if lead.partner_id:
                # Bypass a _prepare_contact_name_from_partner
                lead.contact_name = False if lead.partner_id.is_company else lead.partner_id.name

    @api.depends('partner_id')
    def _compute_partner_name(self):
        for lead in self:
            if lead.partner_id:
                partner = lead.partner_id
                partner_name = partner.parent_id.name
                if not partner_name and partner.is_company:
                    partner_name = partner.name
                elif not partner_name and partner.company_name:
                    partner_name = partner.company_name
                
                # Bypass a _prepare_partner_name_from_partner
                lead.partner_name = partner_name

    @api.depends('partner_id')
    def _compute_partner_address_values(self):
        for lead in self:
            if lead.partner_id:
                partner = lead.partner_id
                # Bypass a _prepare_address_values_from_partner
                # Forzamos la asignación directa de todos los campos, anulando el 'else' nativo
                lead.street = partner.street
                lead.street2 = partner.street2
                lead.city = partner.city
                lead.zip = partner.zip
                lead.state_id = partner.state_id
                lead.country_id = partner.country_id
                
    # ---------------------------------------------------------
    # 2. SOBRESCRIBIR MÉTODOS INVERSE (ROMPER SINCRONIZACIÓN)
    # Reemplazando estos métodos con "pass", desactivamos el 
    # comportamiento nativo que actualiza el res.partner cuando
    # se edita la información desde la vista del crm.lead.
    # ---------------------------------------------------------

    def _inverse_email_from(self):
        pass

    def _inverse_phone(self):
        pass
