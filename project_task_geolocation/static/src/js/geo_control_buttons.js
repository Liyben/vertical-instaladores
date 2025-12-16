/** @odoo-module */
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class GeoControlButtons extends Component {
    static template = "project_task_geolocation.GeoControlButtons";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
    }

    async onGeoAction(actionName) {
        if (!navigator.geolocation) {
            this.notification.add("Geolocalización no disponible.", { type: "danger" });
            return;
        }

        // Feedback visual
        this.notification.add("Obteniendo ubicación...", { type: "info" });

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                try {
                    // Llamamos al método Python (button_start_work o button_end_work)
                    // pasando lat/lng como kwargs
                    const result = await this.orm.call(
                        this.props.record.resModel,
                        actionName,
                        [this.props.record.resId],
                        { lat: lat, lng: lng }
                    );

                    // Si devuelve una acción (como el Wizard en start_work), la ejecutamos
                    if (result && typeof result === 'object' && result.type) {
                        this.actionService.doAction(result);
                    } else {
                        // Si no devuelve acción (stop_work), recargamos la vista
                        await this.props.record.model.load();
                    }

                } catch (e) {
                    console.error("Geo Error:", e);
                    
                    let errorMessage = "Ha ocurrido un error inesperado.";

                    // Caso 1: Error RPC detallado de Odoo (UserError, ValidationError desde Python)
                    // La estructura suele ser e.message.data.message
                    if (e.message && e.message.data && e.message.data.message) {
                        errorMessage = e.message.data.message;
                    }
                    // Caso 2: Error estándar de Javascript o error simple de Odoo
                    // Solo tiene e.message
                    else if (e.message) {
                        errorMessage = e.message;
                    }
                    // Caso 3: Si 'e' es solo un string u otro objeto
                    else {
                        errorMessage = e.toString();
                    }

                    this.notification.add("Error: " + errorMessage, { type: "danger" });
                }
            },
            (err) => {
                this.notification.add("Error GPS: " + err.message, { type: "warning" });
            },
            { enableHighAccuracy: true, timeout: 5000 }
        );
    }
}

export const geoControlButtons = {
    component: GeoControlButtons,
    // Importante: necesitamos 'show_time_control' para saber qué botón pintar
    fieldDependencies: [{ name: "show_time_control", type: "selection" }],
};

registry.category("fields").add("geo_control_buttons", geoControlButtons);