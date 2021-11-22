# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
	_inherit = "res.partner"

	contact_person = fields.Char(string="Contacto Obra")
	contact_mobile = fields.Char()
