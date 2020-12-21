# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from odoo import fields, models, api, _, exceptions

class SaleOrderLine(models.Model):

	_inherit='sale.order.line'

	#Calculo de los valores necesarios para crear el parte de trabajo correspondiente a la linea de pedido
	def _timesheet_create_task_prepare_values(self):
		res = super(SaleOrderLine, self)._timesheet_create_task_prepare_values()

		if res: 
			company_ids = self.env['res.company'].search([('id', '=', res['company_id'])])
			if company_ids:
				for company in company_ids:
					time = res['planned_hours'] * 3600
					laborable_time = company.maximum_hours_per_day
					laborable_days = time // (laborable_time * 3600)
					time = time % (laborable_time * 3600)
					laborable_hours = time // 3600
					time = time % 3600
					laborable_minutes = time // 60
					calculated_date = datetime.now() + timedelta(days=laborable_days,hours=laborable_hours,minutes=laborable_minutes)
			
					#Si es sabado o domingo
					if calculated_date.weekday() == 5 or calculated_date.weekday() == 6:
						calculated_date = calculated_date + timedelta(days=2)
						
					res['date_end'] = calculated_date

		return res