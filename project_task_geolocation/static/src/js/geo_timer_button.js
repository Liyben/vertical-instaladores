/** @odoo-module */
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class GeoTimerButton extends Component {
    static template = "project_task_geolocation.GeoTimerButton";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
    }

    async onGeoClick(actionType) {
        if (!navigator.geolocation) {
            this.notification.add("Navegador sin soporte de geolocalización.", { type: "danger" });
            return;
        }

        // Feedback visual inmediato (opcional)
        this.notification.add("Obteniendo ubicación...", { type: "info" });

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                try {
                    const method = actionType === 'start' ? 'action_geo_timer_start' : 'action_geo_timer_stop';
                    
                    // Llamada al backend
                    await this.orm.call("account.analytic.line", method, [this.props.record.resId], {
                        lat: lat,
                        lng: lng,
                    });
                    
                    // Recargar la vista para actualizar botones
                    await this.props.record.model.load();
                    
                } catch (e) {
                    console.error("Error Geo:", e);
                    this.notification.add("Error al guardar: " + e.message, { type: "danger" });
                }
            },
            (err) => {
                this.notification.add("Error GPS: " + err.message, { type: "warning" });
            },
            { enableHighAccuracy: true, timeout: 5000 }
        );
    }
}

export const geoTimerButton = {
    component: GeoTimerButton,
    fieldDependencies: [{ name: "date_time_end", type: "datetime" }], // Dependencia para saber si está activo
};

registry.category("fields").add("geo_timer_button", geoTimerButton);