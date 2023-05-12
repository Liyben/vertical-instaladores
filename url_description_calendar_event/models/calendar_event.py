# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class Meeting(models.Model):
    _inherit = 'calendar.event'

    def write(self, values):
        url = self.env['ir.config_parameter'].get_param('web.base.url')
        res_id = values.get('res_id')
        res_model = values.get('res_model')
        if res_model and res_id:
            url = url + '/web#id=' + str(res_id) + '&model=' + res_model + '&view_type=form'
            desc = self.description + '\n' + url
            _logger.debug('%s\n', desc)
            _logger.debug('%s\n', url)
            values['description'] = url
        return super(Meeting, self).write(values)
    
