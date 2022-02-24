odoo.define('project_task_geolocation.task_geolocation', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var formController = FormController.include({
        _onButtonClicked: function (event) {
            if(event.data.attrs.name === "button_start_work"){
                alert("Start");
            }
            if(event.data.attrs.name === "button_end_work"){
                alert("Stop.");
            }
            this._super(event);
        },
    });
});