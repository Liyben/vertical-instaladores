# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import re
from odoo import api, fields, models, exceptions, _


class AccountAnalyticLine(models.Model):
	_inherit = "account.analytic.line"

	start_latitude = fields.Float(
		"Start Latitude",
		digits='Geolocalización',
		readonly=True,
	)
	start_longitude = fields.Float(
		"Start Longitude",
		digits='Geolocalización',
		readonly=True,
	)
	end_latitude = fields.Float(
		"End Latitude",
		digits='Geolocalización',
		readonly=True,
	)
	end_longitude = fields.Float(
		"End Longitude",
		digits='Geolocalización',
		readonly=True,
	)

	#Control de los botones para mostrar la geolocalización
	zero_end_control = fields.Boolean(compute='_compute_show_end_geolocation')
	zero_start_control = fields.Boolean(compute='_compute_show_start_geolocation')

	@api.depends('start_latitude','start_longitude')
	def _compute_show_start_geolocation(self):
		for record in self:
			record.zero_start_control = (record.start_latitude == 0.0) and (record.start_longitude == 0.0)

	@api.depends('end_latitude','end_longitude')
	def _compute_show_end_geolocation(self):
		for record in self:
			record.zero_end_control = (record.end_latitude == 0.0) and (record.end_longitude == 0.0)

	def button_start_geolocation(self):
		location = ""  
		for record in self:
			location = "https://maps.google.com/?q=%f,%f" % (record.start_latitude,record.start_longitude)

		return {
			'name' : 'Ubicación',
			'type' : 'ir.actions.act_url',
			'target': 'new',
			'url' : location
		} 

	def button_stop_geolocation(self):
		location = ""  
		for record in self:
			location = "https://maps.google.com/?q=%f,%f" % (record.end_latitude,record.end_longitude)

		return {
			'name' : 'Ubicación',
			'type' : 'ir.actions.act_url',
			'target': 'new',
			'url' : location
		} 

	def button_end_work(self):
		result = super(AccountAnalyticLine, self).button_end_work()
		if result:
			for line in self:
				line.end_latitude = line.task_id.latitude
				line.end_longitude = line.task_id.longitude
		return True

	def unlink(self):
		for record in self:
			if record.task_id:
				record.task_id.show_geolocation_control = 'check-in'

		return super().unlink()