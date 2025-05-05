/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useState } from "@odoo/owl";

export class Geolocation_widget extends Component {
    static template = "geolocation_test.Geolocation_widget";
    static components = {};
    static props = {
        ...standardFieldProps,
    };
    setup() {
      this.state = useState({
        coordinates: {latitude: 0.0, longitude: 0.0},
      });
    }

    getCoordinates() {
      console.log('getCoordinates');
    }
}

const geolocationWidget = {
  displayName: 'Coordinates',
  component: Geolocation_widget,
  supportedTypes: ['json'],
  extractProps: ({ attrs }) => ({
    name: attrs.name,
  }),
};

registry.category("fields").add("latandlong", geolocationWidget);
