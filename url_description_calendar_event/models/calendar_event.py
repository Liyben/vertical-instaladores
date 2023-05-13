# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

import json
import logging
_logger = logging.getLogger(__name__)

class Meeting(models.Model):
    _inherit = 'calendar.event'

    def write(self, values):
        url = self.env['ir.config_parameter'].get_param('web.base.url')
        res_id = self.res_id
        res_model = self.res_model
        if res_model and res_id and 'description' in values:
            action = self.env[self.res_model].browse(self.res_id).get_formview_action()
            _logger.debug('\n\n\n%s\n\n',json.dumps(action, indent = 4))
            url = url + '/web#id=' + str(res_id) + '&model=' + res_model + '&view_type=form'
            desc = values.get('description') + '\n' + url
            values['description'] = desc
        return super(Meeting, self).write(values)
    
