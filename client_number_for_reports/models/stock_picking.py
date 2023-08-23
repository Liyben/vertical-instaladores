# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class StockPicking(models.Model):

	_inherit='stock.picking'

	#Numero de cliente
	customer_code = fields.Char(related='partner_id.ref', readonly=True, string='Nº. Cliente')
	