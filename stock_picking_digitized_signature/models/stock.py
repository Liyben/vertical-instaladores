# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    customer_signature = fields.Binary(string='Firma')
    sign_by = fields.Char(string='Nombre')
    nif = fields.Char(string='DNI')

    @api.model
    def create(self, values):
        stock = super(StockPicking, self).create(values)
        if stock.customer_signature:
            values = {'customer_signature': stock.customer_signature}
            stock._track_signature(values, 'customer_signature')
        return stock

    @api.multi
    def write(self, values):
        self._track_signature(values, 'customer_signature')
        return super(StockPicking, self).write(values)

