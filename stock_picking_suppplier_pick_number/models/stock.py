# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	#Numero de albaran de proveedor
	supplier_pick_number = fields.Char(string='Nº alb. proveedor')