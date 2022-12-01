# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class AccountAnalyticLine(models.Model):
	_inherit = "account.analytic.line"

	#Dominio para el campo mano de obra
	@api.model
	def _get_product_produced_unit_id_domain(self):
		ids = []
		""" for record in self:
			if record.task_id:
				ids = record.task_id.material_ids.mapped('product_id').ids """
		
		return self.env['project.task.material'].search([('task_id.id', '=',12)]).mapped('product_id').ids
		#return [('id', 'in', ids), ('cost_produced_unit', '>', 0)]

	produced_unit = fields.Float(
		"Unidades producidas",
		digits='Product Unit of Measure',
	)
	product_produced_unit_id = fields.Many2one(
		'product.product', 
		string='Producto Unidades Producidas',  
		default=_get_product_produced_unit_id_domain, 
		#check_company=True
	)
	cost_produced_unit = fields.Float(
		string='Coste Unidades Producidas', compute="_compute_cost_produced_unit",
		digits='Product Price', store=True, readonly=False,
		groups="base.group_user"
	)
	total_cost_produced_unit = fields.Float(
		string='Coste Total Unidades Producidas', 
		digits='Product Price', 
		compute="_compute_total_cost_produced_unit"
	)

	@api.depends('product_produced_unit_id', 'company_id', 'currency_id')
	def _compute_cost_produced_unit(self):
		for record in self:
			if not record.product_produced_unit_id:
				record.cost_produced_unit = 0.0
				continue
			record = record.with_company(record.company_id)
			product = record.product_produced_unit_id
			product_cost = product.cost_produced_unit
			if not product_cost:
				if not record.cost_produced_unit:
					record.cost_produced_unit = 0.0
				continue
			fro_cur = product.cost_currency_id
			to_cur = record.currency_id 
			record.cost_produced_unit = fro_cur._convert(
				from_amount=product_cost,
				to_currency=to_cur,
				company=record.company_id or self.env.company,
				date=fields.Date.today(),
				round=False,
			) if to_cur and product_cost else product_cost

	@api.depends('cost_produced_unit','produced_unit')
	def _compute_total_cost_produced_unit(self):
		self.total_cost_produced_unit = 0.0
		for record in self:
			record.total_cost_produced_unit = record.produced_unit * record.cost_produced_unit 

	def _timesheet_postprocess_values(self, values):
		result = super()._timesheet_postprocess_values(values)
		sudo_self = self.sudo()
		if any(field_name in values for field_name in ['product_produced_unit_id', 'cost_produced_unit']):
			for timesheet in sudo_self:
				if timesheet.product_produced_unit_id:
					cost = timesheet.cost_produced_unit or 0.0
					amount = -timesheet.produced_unit * cost
					amount_converted = timesheet.product_produced_unit_id.currency_id._convert(
						amount, timesheet.account_id.currency_id or timesheet.currency_id, self.env.company, timesheet.date)
					result[timesheet.id].update({
						'amount': amount_converted,
					})
		return result