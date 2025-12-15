# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    def button_start_work(self, lat=False, lng=False):
        """ 
        Recibe lat/lng desde JS. 
        Llama al super para obtener la acción del wizard.
        Inyecta lat/lng en el contexto de la acción.
        """
        action = super().button_start_work()
        
        if isinstance(action, dict):
            # --- CORRECCIÓN DEL ERROR JS ---
            # El cliente web necesita 'views' explícitamente cuando se llama desde RPC
            if 'views' not in action:
                # [[False, 'form']] indica que use la vista form por defecto
                action['views'] = [[False, 'form']]
            
            # Inyectamos coordenadas si existen
            if lat and lng:
                if 'context' not in action:
                    action['context'] = {}
                    
                action['context'].update({
                    'default_geo_lat': lat,
                    'default_geo_lng': lng,
                })
                
        return action

    def button_end_work(self, lat=False, lng=False):
        """
        Recibe lat/lng desde JS.
        Busca las líneas activas, les escribe la Geo de parada
        Y luego llama al método original para detenerlas.
        """
        if lat and lng:
            # Buscamos las líneas activas usando la lógica del mixin
            running_lines = self.env["account.analytic.line"].search(
                self._timesheet_running_domain()
            )
            # Escribimos la ubicación ANTES de parar (porque al parar se podría bloquear la edición)
            if running_lines:
                running_lines.write({
                    'geo_stop_lat': lat,
                    'geo_stop_lng': lng
                })
        
        return super().button_end_work()