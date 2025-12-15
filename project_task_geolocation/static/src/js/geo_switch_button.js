/** @odoo-module */
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class GeoSwitchButton extends Component {
    static template = "project_task_geolocation.GeoSwitchButton";
    static props = { ...standardFieldProps };

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");
    }

    async onSwitchClick() {
        if (!navigator.geolocation) {
            this.submitWizard(false, false);
            return;
        }
        
        this.notification.add("Obteniendo ubicación...", { type: "info" });

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                await this.submitWizard(lat, lng);
            },
            (err) => {
                this.notification.add("No se pudo obtener GPS, continuando sin ubicación.", { type: "warning" });
                this.submitWizard(false, false);
            },
            { enableHighAccuracy: true, timeout: 5000 }
        );
    }

    async submitWizard(lat, lng) {
        try {
            // Guardar coords en el modelo transient
            if (lat && lng) {
                await this.props.record.update({
                    geo_lat: lat,
                    geo_lng: lng,
                });
            }

            // Guardar registro (save)
            await this.props.record.save();

            // Ejecutar método Python
            const action = await this.orm.call(
                this.props.record.resModel,
                "action_switch",
                [this.props.record.resId]
            );

            // Ejecutar la acción devuelta (cerrar ventana/recargar)
            if (action) {
                this.actionService.doAction(action);
            } else {
                this.actionService.doAction({ type: 'ir.actions.act_window_close' });
            }
        } catch (e) {
            this.notification.add("Error en wizard: " + e.message, { type: "danger" });
        }
    }
}

export const geoSwitchButton = {
    component: GeoSwitchButton,
};

// Usamos "view_widgets" porque en el XML usamos la etiqueta <widget>
registry.category("view_widgets").add("geo_switch_button", geoSwitchButton);