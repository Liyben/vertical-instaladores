# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class Meeting(models.Model):
    _inherit = 'calendar.event'

    def write(self, values):
        res = super().write(values)
        url = self.env['ir.config_parameter'].get_param('web.base.url')
        if self.res_model and self.res_id:
            action = self.env[self.res_model].browse(self.res_id).get_formview_action()
            url = url + '/web#id=' + str(self.res_id) + '&model=' + self.res_model + '&view_type=form'
            _logger.debug('%s\n', url)
        return res