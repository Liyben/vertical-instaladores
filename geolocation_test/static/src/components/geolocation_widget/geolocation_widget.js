/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState } from "@odoo/owl";

export class GeolocationWidget extends Component {
    static template = "geolocation_test.GeolocationWidget";
    static components = {};
    static props = {
        ...standardFieldProps,
    };
    setup() {
      this.state = useState({
        coordinates: { latitude: 0.0, longitude: 0.0 },
      });
    }

    getCoordinates() {
      console.log('getCoordinates');
    }
}

const geolocationWidget = {
  displayName: 'Coordinates',
  component: GeolocationWidget,
  supportedTypes: ['json'],
  extractProps: ({ attrs }) => ({
    name: attrs.name,
  }),
};

registry.category("fields").add("latandlong", geolocationWidget);
