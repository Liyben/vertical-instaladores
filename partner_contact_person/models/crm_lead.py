# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _


class CrmLead(models.Model):
	_inherit = 'crm.lead'
	
	contact_person = fields.Char(string="Contacto Obra")
	contact_mobile = fields.Char()

	@api.onchange('contact_mobile', 'country_id', 'company_id')
	def _onchange_contact_mobile_validation(self):
		if self.contact_mobile:
			self.contact_mobile = self.phone_format(self.contact_mobile)

	def _prepare_contact_name_from_partner(self, partner):
		result = super()._prepare_contact_name_from_partner(partner)
		result.update(
			{
				"contact_person": self.contact_person if self.contact_person else partner.contact_person,
				"contact_mobile": self.contact_mobile if self.contact_mobile else partner.contact_mobile,
			}
		)
		return result