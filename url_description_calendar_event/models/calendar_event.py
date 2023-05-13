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
		result = super(Meeting, self).create(vals_list)
		url = self.env['ir.config_parameter'].get_param('web.base.url')
		res_id = result['res_id']
		res_model = result['res_model']
		if res_model and res_id:
			url = url + '/web#id=' + str(res_id) + '&model=' + res_model + '&view_type=form'
			desc = result['description'] + '\n' + url
			result['description'] = desc
		return result