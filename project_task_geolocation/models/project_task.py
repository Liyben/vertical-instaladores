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
        # 1. Llamamos al original para que haga sus comprobaciones (permisos, etc.)
        action = super().button_start_work()
        
        # 2. Si devuelve un diccionario (la acción), la enriquecemos
        if isinstance(action, dict) and action.get('type') == 'ir.actions.act_window':
            
            # Buscamos explícitamente la vista del módulo OCA para evitar errores de resolución
            # El ID externo suele ser 'project_timesheet_time_control.hr_timesheet_switch_form'
            # pero usaremos search para ser más seguros o fallback a False
            view_id = self.env.ref('project_timesheet_time_control.hr_timesheet_switch_form', raise_if_not_found=False)
            view_id = view_id.id if view_id else False

            # Forzamos la estructura 'views' que JS necesita obligatoriamente
            action['views'] = [[view_id, 'form']]
            
            # Aseguramos que sea un modal ('new')
            action['target'] = 'new'

            # 3. Inyectar coordenadas en el contexto
            if lat and lng:
                if 'context' not in action:
                    action['context'] = {}
                
                # Usamos update para no borrar lo que ya traiga la OCA
                action['context'].update({
                    'default_geo_lat': lat,
                    'default_geo_lng': lng,
                    # Aseguramos valores por defecto críticos del wizard
                    'default_project_id': self.project_id.id,
                    'default_task_id': self.id,
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