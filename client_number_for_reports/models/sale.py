# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.addons import decimal_precision as dp
from odoo.tools import float_is_zero, float_compare

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	"""docstring for SaleOrder"""
	_inherit='sale.order'

	#Numero de cliente
	ref = fields.Char(related='partner_id.ref', readonly=True, string='Nº. Cliente')
