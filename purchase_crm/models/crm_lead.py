# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class CrmLead(models.Model):
	_inherit = 'crm.lead'

	purchase_amount_total = fields.Monetary(compute='_compute_purchase_data', string="Total de compras", help="Total sin impuestos de las compras hechas", currency_field='company_currency')
	rfq_count = fields.Integer(compute='_compute_purchase_data', string="Número de solicitudes de compra")
	purchase_order_count = fields.Integer(compute='_compute_purchase_data', string="Número de pedidos de compra")
	po_ids = fields.One2many('purchase.order', 'opportunity_id', string='Purchase Orders')

	@api.depends('po_ids.state', 'po_ids.currency_id', 'po_ids.amount_untaxed', 'po_ids.date_approve', 'po_ids.company_id')
	def _compute_purchase_data(self):
		for lead in self:
			total = 0.0
			rfq_cnt = 0
			purchase_order_cnt = 0
			company_currency = lead.company_currency or self.env.company.currency_id
			for order in lead.po_ids:
				if order.state in ('draft','sent'):
					rfq_cnt += 1
				if order.state not in ('draft','sent'):
					purchase_order_cnt += 1
					total += order.currency_id._convert(
						order.amount_untaxed, company_currency, order.company_id, order.date_approve or fields.Date.today())
			lead.purchase_amount_total = total
			lead.rfq_count = rfq_cnt
			lead.purchase_order_count = purchase_order_cnt

	def action_view_purchase_rfq(self):
		action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
		action['context'] = {
			'quotation_only': True,
			'default_opportunity_id': self.id
		}
		action['domain'] = [('opportunity_id', '=', self.id)]
		rfqs = self.mapped('po_ids').filtered(lambda l: l.state in ('draft', 'sent'))
		if len(rfqs) == 1:
			action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
			action['res_id'] = rfqs.id
		return action

	def action_view_purchase_order(self):
		action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")
		action['context'] = {
			'default_opportunity_id': self.id,
		}
		action['domain'] = [('opportunity_id', '=', self.id), ('state','in',('purchase', 'done'))]
		orders = self.mapped('po_ids').filtered(lambda l: l.state not in ('draft', 'sent', 'cancel'))
		if len(orders) == 1:
			action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
			action['res_id'] = orders.id
		return action