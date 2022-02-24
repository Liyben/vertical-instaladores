odoo.define('project_task_geolocation.task_geolocation', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var formController = FormController.include({
        update_task: function () {
            var self = this;
            var options = {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 60000,
            };
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    self._get_geolocation.bind(self),
                    self._getPositionError.bind(self),
                    options
                );
            }
        },
        _get_geolocation: function (position) {
            var self = this;
            this._rpc({
                model: "project.task",
                method: "get_current_geolocation",
                args: [[this.res_id], [position.coords.latitude, position.coords.longitude]],
            }).then(function (result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.do_warn(result.warning);
                }
                console.log('https://maps.google.com/?q='+ position.coords.latitude+','+ position.coords.longitude);
            });
        },
        _getPositionError: function (error) {
            console.warn("ERROR(" + error.code + "): " + error.message);
            const position = {
                coords: {
                    latitude: 0.0,
                    longitude: 0.0,
                },
            };
            this._get_geolocation(position);
        },
        _onButtonClicked: function (event) {
            if(event.data.attrs.name === "button_start_work"){
                console.log("Start.");
                this.update_task();
            }
            if(event.data.attrs.name === "button_end_work"){
                console.log("Stop.");
                this.update_task();
            }
            this._super(event);
        },
    });
});