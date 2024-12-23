# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, modules, tools, _


class Module(models.Model):
    _inherit = "ir.module.module"
    
    @api.model
    def get_apps_server(self):
        return tools.config.get('apps_server', 'https://apps.odoo.com/apps')

