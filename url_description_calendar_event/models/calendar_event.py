# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

import json
import pytz
from odoo import tools

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
	
	def _sync_activities(self, fields):
		# update activities
		_logger.debug('%s\n',json.dumps(fields, indent=4))
		for event in self:
			if event.activity_ids:
				activity_values = {}
				if 'name' in fields:
					activity_values['summary'] = event.name
				if 'description' in fields:
					activity_values['note'] = event.description and tools.plaintext2html(event.description)
				if 'start' in fields:
					# self.start is a datetime UTC *only when the event is not allday*
					# activty.date_deadline is a date (No TZ, but should represent the day in which the user's TZ is)
					# See 72254129dbaeae58d0a2055cba4e4a82cde495b7 for the same issue, but elsewhere
					deadline = event.start
					user_tz = self.env.context.get('tz')
					if user_tz and not event.allday:
						deadline = pytz.UTC.localize(deadline)
						deadline = deadline.astimezone(pytz.timezone(user_tz))
					activity_values['date_deadline'] = deadline.date()
				if 'user_id' in fields:
					activity_values['user_id'] = event.user_id.id
				if activity_values.keys():
					event.activity_ids.write(activity_values)