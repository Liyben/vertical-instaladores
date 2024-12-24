# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import requests
import logging
import json

from odoo import api, fields, models, modules, tools, _
from odoo.service.common import exp_version
from odoo.addons.base_import_module.models.ir_module import APPS_URL
from odoo.release import major_version

_logger = logging.getLogger(__name__)
class Module(models.Model):
    _inherit = "ir.module.module"
    
    def update_published_version(self):
        modules_to_update_dict = self.get_modules_need_update()
        if not modules_to_update_dict:
            _logger.debug("NOT LIST\n")
            return False
        
        # Update published_version field
        _logger.debug("LIST: %s\n", str(modules_to_update_dict))
        return True
    
    def check_app_store_updates(self, modules,fields):
        """Check for updates in the app store for the given modules.

        Args:
            modules (dict): A dictionary of installed modules.

        Returns:
            dict: Information about the modules on the odoo server.
            Example:
            {
                'module.name': {
                    'id': 123,  # module ID
                    'name': 'example_module',  # module name
                    'version_local_running': '1.0.0',  # local version
                    'version_local_downloaded': '1.0.0',  # downloaded version
                    'version_remote': '1.2.0',  # version available in odoo app store
                    'todo': 'to_update',  # Indicates that an update is needed
                },
            }
        """
        # odoo apps server
        url = f"{APPS_URL}/apps/embed/update"
        #url = f"{APPS_URL}/loempia/listdatamodules"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "headers": headers,
            "params": {
                "modules": modules,
                "version": exp_version(),
            },
        }
        """ payload = {
            'params': {
                'series': major_version,
                'module_fields': fields,
                'module_type': 'official',
                'module_name': self.env.context.get('module_name'),
                'domain': None,
                'limit': None,
                'offset': None,
            }
        } """
        #resp = self._call_apps(json.dumps(payload))
        #resp.raise_for_status()
        #modules_list = resp.json().get('result', [])
        response = requests.Session().post(url, json=payload).json()
        _logger.debug("RESPONSE: %s\n", str(response.get("result")))
        return response.get("result")

    def get_modules_need_update(self):
        """Find installed modules and get a dictionary of modules that need an update.

        Returns:
            dict: Modules that need an update.
            Example:
            {
                'module.name': {
                    'id': 123,  # module ID on the odoo server
                    'name': 'example_module',  # module name
                    'version_local_running': '1.0.0',  # local version
                    'version_local_downloaded': '1.0.0',  # downloaded version
                    'version_remote': '1.2.0',  # version available in odoo app store
                    'todo': 'to_update',  # Indicates that an update is needed
                    'display_name': 'Example Module',  # display name
                },
            }
        """
        # find the installed modules and prepare the dictionary
        # for the query on the server
        fields = [
                "id",
                "name",
                "installed_version",
                "latest_version",
                "state",
                "display_name",
            ]
        installed_modules = self.search_read(
            [("state", "=", "installed")],
            fields=fields,
        )
        modules_dict = {record["name"]: record for record in installed_modules}
        _logger.debug("MODULES DICT: %s\n", str(modules_dict))
        # Check for updates
        modules_to_update_dict = self.check_app_store_updates(modules_dict, fields)

        return modules_to_update_dict
