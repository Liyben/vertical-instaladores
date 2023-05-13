# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class Meeting(models.Model):
	_inherit = 'calendar.event'

	def write(self, values):
		url = self.env['ir.config_parameter'].get_param('web.base.url')
		res_id = self.res_id
		res_model = self.res_model
		if res_model and res_id and 'description' in values:
			url = url + '/web#id=' + str(res_id) + '&model=' + res_model + '&view_type=form'
			desc = values.get('description') + '\n' + url
			values['description'] = desc
		return super(Meeting, self).write(values)
	
	@api.model_create_multi
	def create(self, vals_list):
		self = self.with_context(is_calendar_event_new=True)
		defaults = self.default_get(['activity_ids', 'res_model_id', 'res_id', 'res_model', 'description'])
		meeting_activity_type = self.env['mail.activity.type'].search([('category', '=', 'meeting')], limit=1)
		# get list of models ids and filter out None values directly
		model_ids = list(filter(None, {values.get('res_model_id', defaults.get('res_model_id')) for values in vals_list}))
		model_name = defaults.get('res_model')
		valid_activity_model_ids = model_name and self.env[model_name].sudo().browse(model_ids).filtered(lambda m: 'activity_ids' in m).ids or []
		if meeting_activity_type and not defaults.get('activity_ids'):
			for values in vals_list:
				# created from calendar: try to create an activity on the related record
				if values.get('activity_ids'):
					continue
				res_model_id = values.get('res_model_id', defaults.get('res_model_id'))
				values['res_id'] = res_id = values.get('res_id') or defaults.get('res_id')
				url = self.env['ir.config_parameter'].get_param('web.base.url')
				if res_model_id and res_id:
					url = url + '/web#id=' + str(res_id) + '&model=' + res_model_id + '&view_type=form'
					desc = values.get('description') or defaults.get('description')
					values['description'] = desc + '\n' + url
		return super(Meeting, self).create(vals_list)