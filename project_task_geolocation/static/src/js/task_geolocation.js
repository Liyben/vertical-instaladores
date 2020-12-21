odoo.define('project_task_geolocation.task_geolocation', function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var time = require('web.time');
    var FieldManagerMixin = require('web.FieldManagerMixin');
    
    var _t = core._t;
    
    var MyGeolocation  = AbstractField.extend({
    
        init: function () {
            this._super.apply(this, arguments);
            this.location = (null, null);
            this.errorCode = null;
        },
    
        willStart: function () {
            var self = this;
            var options = {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            };
            var def = this._rpc({
                model: 'project.task',
                method: 'search_read',
                args: [[['id', '=', this.res_id]]],
            })
            .then(function (res) {
                
            });
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(self._manual_geolocation.bind(self), self._getPositionError, options);
            }
            return $.when(this._super.apply(this, arguments), def);
        },
        _manual_geolocation: function (position) {
            var self = this;
            this._rpc({
                model: 'project.task',
                method: 'manual_geolocation',
                args: [[this.res_id], [position.coords.latitude, position.coords.longitude]],
            }).then(function(result) {
                console.log('https://maps.google.com/?q='+ position.coords.latitude+','+ position.coords.longitude);
            });        
        },
        _getPositionError: function (error) {
            console.warn('ERROR(${error.code}): ${error.message}');
        },
    });
    field_registry.add('geolocation_uoms', MyGeolocation);
    });
    
