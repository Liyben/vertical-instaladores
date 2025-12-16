/** @odoo-module */
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillDestroy } from "@odoo/owl"; 
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class GeoControlButtons extends Component {
    static template = "project_task_geolocation.GeoControlButtons";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
        
        // --- PROTECCIÓN COMPONENT DESTROYED ---
        this.isAlive = true;
        onWillDestroy(() => {
            this.isAlive = false;
        });
    }

    async onGeoAction(actionName) {
        if (!navigator.geolocation) {
            this.notification.add("Geolocalización no disponible.", { type: "danger" });
            return;
        }

        this.notification.add("Obteniendo ubicación...", { type: "info" });

        // Opciones GPS: Timeout de 20s para asegurar que el móvil tiene tiempo de triangular
        const options = { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 };

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                // 1. Si el componente murió mientras esperábamos el GPS, paramos.
                if (!this.isAlive) return;

                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                try {
                    // Llamada al servidor (Python)
                    const result = await this.orm.call(
                        this.props.record.resModel,
                        actionName,
                        [this.props.record.resId],
                        { lat: lat, lng: lng }
                    );

                    // --- DEBUG: Muestra en la consola (F12) qué devolvió Python ---
                    console.log("Respuesta del servidor (Geo):", result);
                    // -----------------------------------------------------------

                    // 2. Volvemos a comprobar la vida del componente tras el await
                    if (!this.isAlive) return;

                    // Lógica para abrir Wizard o Recargar
                    if (result && typeof result === 'object' && result.type) {
                        // Si Python devuelve una acción (Start -> Wizard), la ejecutamos
                        await this.actionService.doAction(result, {
                            onClose: async () => {
                                // Esta función se ejecuta AUTOMÁTICAMENTE cuando el Wizard se cierra
                                if (this.isAlive) {
                                    // Forzamos la recarga de la Tarea para ver la nueva línea y el cambio de botón
                                    await this.props.record.model.load();
                                }
                            }
                        });
                    } else {
                        // Si no devuelve acción (Stop), simplemente recargamos los datos
                        await this.props.record.model.load();
                    }

                } catch (e) {
                    if (!this.isAlive) return; // Protección en el catch
                    
                    console.error("Geo Error:", e);
                    let errorMessage = "Ha ocurrido un error inesperado.";

                    // Manejo robusto de mensajes de error
                    if (e.message && e.message.data && e.message.data.message) {
                        errorMessage = e.message.data.message;
                    } else if (e.message) {
                        errorMessage = e.message;
                    } else {
                        errorMessage = e.toString();
                    }
                    this.notification.add("Error: " + errorMessage, { type: "danger" });
                }
            },
            (err) => {
                if (!this.isAlive) return; // Protección en error GPS
                
                let msg = err.message;
                // Mensajes más amigables para errores comunes
                if (err.code === 1) msg = "Permiso de ubicación denegado.";
                if (err.code === 3) msg = "Tiempo de espera agotado (Timeout).";
                
                this.notification.add("Error GPS: " + msg, { type: "warning" });
            },
            options
        );
    }
}

export const geoControlButtons = {
    component: GeoControlButtons,
    fieldDependencies: [{ name: "show_time_control", type: "selection" }],
};

registry.category("fields").add("geo_control_buttons", geoControlButtons);