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
        
        this.isAlive = true;
        onWillDestroy(() => {
            this.isAlive = false;
        });
    }

    async onGeoAction(actionName) {
        if (!navigator.geolocation) {
            alert("Tu navegador no soporta geolocalización.");
            return;
        }

        // Aviso visual para saber que el botón funcionó
        this.notification.add("Buscando satélites... (Espera 20s)", { type: "info" });

        const options = {
            enableHighAccuracy: true,
            timeout: 20000, // AUMENTADO A 20 SEGUNDOS
            maximumAge: 0
        };

        navigator.geolocation.getCurrentPosition(
            // --- ÉXITO ---
            async (position) => {
                if (!this.isAlive) return;
                
                // Alert para confirmar que obtuvo coordenadas (Borrar en producción)
                // alert("Coords: " + position.coords.latitude); 

                try {
                    const result = await this.orm.call(
                        this.props.record.resModel,
                        actionName,
                        [this.props.record.resId],
                        { 
                            lat: position.coords.latitude, 
                            lng: position.coords.longitude 
                        }
                    );

                    if (!this.isAlive) return;

                    if (result && typeof result === 'object' && result.type) {
                        this.actionService.doAction(result);
                    } else {
                        await this.props.record.model.load();
                    }

                } catch (e) {
                    if (!this.isAlive) return;
                    alert("Error Servidor: " + e.toString());
                }
            },
            // --- ERROR DE GPS ---
            (err) => {
                if (!this.isAlive) return;
                
                // DIAGNÓSTICO: Esto te dirá exactamente qué pasa en el iPhone
                let errorMsg = "";
                switch(err.code) {
                    case 1: errorMsg = "PERMISO DENEGADO. Revisa Ajustes > Privacidad."; break;
                    case 2: errorMsg = "POSICIÓN NO DISPONIBLE. (Mala señal GPS)."; break;
                    case 3: errorMsg = "TIMEOUT. Se acabó el tiempo de espera."; break;
                    default: errorMsg = "Error desconocido: " + err.message;
                }
                
                // Usamos alert para que lo veas sí o sí en el móvil
                alert("Error GPS: " + errorMsg);
                this.notification.add(errorMsg, { type: "danger" });
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