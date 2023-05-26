odoo.define('systray.odoo_version', function(require) {
    "use strict";
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var ActionMenu = Widget.extend({
        template: 'systray_odoo_version',
        /* events: {
            'click .help_icon': 'onclick_help_icon',
        },
        onclick_help_icon: function() {
            var self = this;
            self.do_action({
                name: 'Help form',
                res_model: 'help.icons',
                views: [[false, 'form']],
                type: 'ir.actions.act_window',
                view_mode: 'form',
                target: 'new'
            });
        }, */
    });
    SystrayMenu.Items.push(ActionMenu);
    return ActionMenu;
});