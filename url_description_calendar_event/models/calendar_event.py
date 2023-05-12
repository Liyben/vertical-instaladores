# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class Meeting(models.Model):
    _inherit = 'calendar.event'

    def write(self, values):
        res = super(Meeting, self).write(values)
        url = self.env['ir.config_parameter'].get_param('web.base.url')
        if self.res_model and self.res_id:
            url = url + '/web#id=' + str(self.res_id) + '&model=' + self.res_model + '&view_type=form'
            desc = self.description + '\n' + url
            _logger.debug('%s\n', desc)
            _logger.debug('%s\n', url)
            #self.description = desc
        return res
    
