# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

class HrTimesheetSwitch(models.TransientModel):
    _inherit = 'hr.timesheet.switch'

    geo_lat = fields.Float(digits=(10, 7))
    geo_lng = fields.Float(digits=(10, 7))

    def action_switch(self):
        """ Sobrescribe el cambio de tarea para inyectar coordenadas """
        res = super().action_switch()
        
        # 1. Actualizar la tarea que se acaba de cerrar (STOP)
        closed_line = self.env['account.analytic.line'].search([
            ('user_id', '=', self.env.user.id),
            ('date_time_end', '!=', False)
        ], limit=1, order='date_time_end desc')
        
        if closed_line and self.geo_lat and self.geo_lng:
            closed_line.write({
                'geo_stop_lat': self.geo_lat,
                'geo_stop_lng': self.geo_lng
            })

        # 2. Actualizar la nueva tarea iniciada (START)
        new_line = self.env['account.analytic.line'].search([
            ('user_id', '=', self.env.user.id),
            ('date_time_end', '=', False)
        ], limit=1, order='date_time desc')

        if new_line and self.geo_lat and self.geo_lng:
            new_line.write({
                'geo_start_lat': self.geo_lat,
                'geo_start_lng': self.geo_lng
            })
            
        return res