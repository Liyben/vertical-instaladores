# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta
from odoo import fields, models, api, _, exceptions

class ProjectTask(models.Model):
	_inherit = 'project.task'

	date_end = fields.Datetime(string='Ending Date', default=fields.Datetime.now, index=True, copy=False)

	@api.multi
	@api.onchange('date_start','planned_hours')
	def _onchange_date_start_planned_hours(self):
		for task in self:
			if task.date_start:
				#Calculo de la fecha fin
				time = task.planned_hours * 3600
				laborable_time = task.company_id.maximum_hours_per_day
				laborable_days = time // (laborable_time * 3600)
				time = time % (laborable_time * 3600)
				laborable_hours = time // 3600
				time = time % 3600
				laborable_minutes = time // 60
				calculated_date = fields.Datetime.from_string(task.date_start) + timedelta(days=laborable_days,hours=laborable_hours,minutes=laborable_minutes)
				#Si es sabado o domingo
				if calculated_date.weekday() == 5 or calculated_date.weekday() == 6:
					calculated_date = calculated_date + timedelta(days=2)
						
				task.date_end = calculated_date
			else:
				raise exceptions.ValidationError('Debe seleccionar una fecha de inicio.')

