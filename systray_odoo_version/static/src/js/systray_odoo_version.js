/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import {Dropdown} from '@web/core/dropdown/dropdown';
import {DropdownItem} from '@web/core/dropdown/dropdown_item';

class SystrayVersionMenu extends Component {
   setup() {
       super.setup(...arguments);
       this.action = useService("action");
   }
}

SystrayVersionMenu.template = "systray_odoo_version.SystrayVersionMenu";
SystrayVersionMenu.components = { Dropdown, DropdownItem };

export const systrayItem = { Component: SystrayVersionMenu, };

registry.category("systray").add("SystrayVersionMenu", systrayItem, { sequence: 1 });
