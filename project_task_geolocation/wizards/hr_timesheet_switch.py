# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

class HrTimesheetSwitch(models.TransientModel):
    _inherit = 'hr.timesheet.switch'

    # Campos para recibir las coordenadas desde el contexto (botón de la tarea)
    geo_lat = fields.Float(digits=(10, 7))
    geo_lng = fields.Float(digits=(10, 7))

    def action_switch(self):
        """ 
        Sobrescribimos para gestionar la geolocalización.
        1. Inyectamos GEO STOP en el timer antiguo (si existe).
        2. Ejecutamos la lógica original (para, copia/crea, arranca).
        3. Inyectamos GEO START en el nuevo timer.
        """
        
        # --- PASO 1: Gestionar el Timer Antiguo (STOP) ---
        # El wizard ya sabe cuál es el timer corriendo gracias al campo 'running_timer_id'
        if self.running_timer_id and self.geo_lat and self.geo_lng:
            # Escribimos las coordenadas ANTES de que super() cierre la línea.
            self.running_timer_id.write({
                'geo_stop_lat': self.geo_lat,
                'geo_stop_lng': self.geo_lng
            })

        # --- PASO 2: Ejecutar lógica original de la OCA ---
        # Esto detendrá running_timer_id y creará una nueva línea
        res = super().action_switch()

        # --- PASO 3: Gestionar el Nuevo Timer (START) ---
        # La lógica original no devuelve el objeto 'new', devuelve una acción o nada.
        # Pero sabemos que acaba de crear una línea ACTIVA para este usuario.
        
        # Estrategia A: Si super() devuelve una acción de ventana con res_id (caso 'show_created_timer')
        new_line = False
        if isinstance(res, dict) and res.get('res_id') and res.get('res_model') == 'account.analytic.line':
            new_line = self.env['account.analytic.line'].browse(res['res_id'])
        
        # Estrategia B: Si no devuelve acción (comportamiento por defecto), buscamos la última creada
        if not new_line:
            new_line = self.env['account.analytic.line'].search([
                ('user_id', '=', self.env.user.id),
                ('date_time_end', '=', False) # Buscamos la que está CORRIENDO
            ], limit=1, order='id desc')

        # Si encontramos la nueva línea y tenemos coordenadas, guardamos el START
        if new_line and self.geo_lat and self.geo_lng:
            new_line.write({
                'geo_start_lat': self.geo_lat,
                'geo_start_lng': self.geo_lng
            })

        return res