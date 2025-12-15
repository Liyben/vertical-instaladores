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
                    console.error(e);
                    this.notification.add("Error en servidor: " + e.message.data.message, { type: "danger" });
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

registry.category("view_widgets").add("geo_control_buttons", geoControlButtons);