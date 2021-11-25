# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

	opportunity_id = fields.Many2one('crm.lead', string='Oportunidad / Aviso', check_company=True, 
		domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")