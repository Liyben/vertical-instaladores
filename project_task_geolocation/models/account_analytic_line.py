# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    geo_start_lat = fields.Float(string='Latitud Inicio', digits=(10, 7), readonly=True)
    geo_start_lng = fields.Float(string='Longitud Inicio', digits=(10, 7), readonly=True)
    geo_stop_lat = fields.Float(string='Latitud Fin', digits=(10, 7), readonly=True)
    geo_stop_lng = fields.Float(string='Longitud Fin', digits=(10, 7), readonly=True)

    def action_geo_timer_start(self, lat=False, lng=False):
        """ Inicia el timer y guarda coordenadas """
        # Ejecuta la lógica original de OCA
        res = self.button_resume_work()
        
        # Busca la línea activa recién creada para el usuario actual
        domain = [('user_id', '=', self.env.user.id), ('date_time_end', '=', False)]
        running_line = self.search(domain, limit=1, order='id desc')
        
        if running_line and lat and lng:
            running_line.write({
                'geo_start_lat': lat,
                'geo_start_lng': lng
            })
        return res

    def action_geo_timer_stop(self, lat=False, lng=False):
        """ Detiene el timer y guarda coordenadas """
        if lat and lng:
            self.write({
                'geo_stop_lat': lat,
                'geo_stop_lng': lng
            })
        return self.button_end_work()