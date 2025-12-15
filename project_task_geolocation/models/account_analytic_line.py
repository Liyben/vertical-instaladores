# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    geo_start_lat = fields.Float(string='Latitud Inicio', digits=(10, 7), readonly=True)
    geo_start_lng = fields.Float(string='Longitud Inicio', digits=(10, 7), readonly=True)
    geo_stop_lat = fields.Float(string='Latitud Fin', digits=(10, 7), readonly=True)
    geo_stop_lng = fields.Float(string='Longitud Fin', digits=(10, 7), readonly=True)

    def _get_google_maps_url(self, lat, lng):
        """ Helper para construir la URL """
        return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

    def action_view_geo_start(self):
        self.ensure_one()
        if self.geo_start_lat and self.geo_start_lng:
            return {
                'type': 'ir.actions.act_url',
                'url': self._get_google_maps_url(self.geo_start_lat, self.geo_start_lng),
                'target': 'new',
            }

    def action_view_geo_stop(self):
        self.ensure_one()
        if self.geo_stop_lat and self.geo_stop_lng:
            return {
                'type': 'ir.actions.act_url',
                'url': self._get_google_maps_url(self.geo_stop_lat, self.geo_stop_lng),
                'target': 'new',
            }