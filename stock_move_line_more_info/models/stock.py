# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class StockMoveLine(models.Model):
	_inherit = 'stock.move.line'

	#Empresa
	partner_id = fields.Many2one('res.partner', related='picking_id.partner_id', readonly=True, string='Empresa')
