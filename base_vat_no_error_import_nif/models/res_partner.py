# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _, exceptions

class ResPartner(models.Model):
	_inherit = 'res.partner'
	
	def check_vat_es(self, vat):
		return True