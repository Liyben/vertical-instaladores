# © 2023 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

from odoo.http import request
from odoo import http

import logging
_logger = logging.getLogger(__name__)

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def action_create_calendar_event(self):
        action = super(MailActivity, self).action_create_calendar_event()
        _logger.debug('%s\n', request.httprequest.url)
        _logger.debug('%s\n', request.httprequest.base_url)
        _logger.debug('%s\n', request.httprequest.host_url)
        _logger.debug('%s\n', http.request.httprequest)
        _logger.debug('%s\n', http.request.httprequest.full_path)
        _logger.debug('%s\n', request.httprequest.referrer)

        return action