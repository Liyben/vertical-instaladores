# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _, exceptions

class ResPartner(models.Model):
	_inherit = 'res.partner'
	
	@api.constrains('vat', 'country_id')
	def check_vat(self):
		return True