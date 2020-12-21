# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import re
import datetime
import tempfile
import logging
import os
import jinja2
import json
import sys

import werkzeug
from werkzeug.urls import url_decode, iri_to_uri
from collections import OrderedDict

import odoo
from odoo.api import call_kw, Environment
from odoo.tools import crop_image, topological_sort, html_escape, pycompat
from odoo.addons.web.controllers.main import Database
from odoo import http
from werkzeug.exceptions import BadRequest
from odoo.http import content_disposition, dispatch_rpc, request, \
	serialize_exception as _serialize_exception, Response
from odoo.service import db
from odoo.tools.misc import str2bool, xlwt, file_open
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

if hasattr(sys, 'frozen'):
	# When running on compiled windows binary, we don't have access to package loader.
	path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
	loader = jinja2.FileSystemLoader(path)
else:
	loader = jinja2.PackageLoader('odoo.addons.web_database_manager', "views")

env = jinja2.Environment(loader=loader, autoescape=True)
env.filters["json"] = json.dumps

DBNAME_PATTERN = '^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'

#----------------------------------------------------------
# Odoo Web helpers
#----------------------------------------------------------

db_list = http.db_list

db_monodb = http.db_monodb

def abort_and_redirect(url):
    r = request.httprequest
    response = werkzeug.utils.redirect(url, 302)
    response = r.app.get_response(r, response, explicit_session=False)
    werkzeug.exceptions.abort(response)

def ensure_db(redirect='/web/v2/selector'):
    # This helper should be used in web client auth="none" routes
    # if those routes needs a db to work with.
    # If the heuristics does not find any database, then the users will be
    # redirected to db selector or any url specified by `redirect` argument.
    # If the db is taken out of a query parameter, it will be checked against
    # `http.db_filter()` in order to ensure it's legit and thus avoid db
    # forgering that could lead to xss attacks.
    db = request.params.get('db') and request.params.get('db').strip()

    # Ensure db is legit
    if db and db not in http.db_filter([db]):
        db = None

    if db and not request.session.db:
        # User asked a specific database on a new session.
        # That mean the nodb router has been used to find the route
        # Depending on installed module in the database, the rendering of the page
        # may depend on data injected by the database route dispatcher.
        # Thus, we redirect the user to the same page but with the session cookie set.
        # This will force using the database route dispatcher...
        r = request.httprequest
        url_redirect = werkzeug.urls.url_parse(r.base_url)
        if r.query_string:
            # in P3, request.query_string is bytes, the rest is text, can't mix them
            query_string = iri_to_uri(r.query_string)
            url_redirect = url_redirect.replace(query=query_string)
        request.session.db = db
        abort_and_redirect(url_redirect)

    # if db not provided, use the session one
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db

    # if no database provided and no database in session, use monodb
    if not db:
        db = db_monodb(request.httprequest)

    # if no db can be found til here, send to the database selector
    # the database selector will redirect to database manager if needed
    if not db:
        werkzeug.exceptions.abort(werkzeug.utils.redirect(redirect, 303))

    # always switch the session to the computed db
    if db != request.session.db:
        request.session.logout()
        abort_and_redirect(request.httprequest.url)

    request.session.db = db

def module_installed(environment):
    # Candidates module the current heuristic is the /static dir
    loadable = list(http.addons_manifest)

    # Retrieve database installed modules
    # TODO The following code should move to ir.module.module.list_installed_modules()
    Modules = environment['ir.module.module']
    domain = [('state','=','installed'), ('name','in', loadable)]
    modules = OrderedDict(
        (module.name, module.dependencies_id.mapped('name'))
        for module in Modules.search(domain)
    )

    sorted_modules = topological_sort(modules)
    return sorted_modules

def module_installed_bypass_session(dbname):
    try:
        registry = odoo.registry(dbname)
        with registry.cursor() as cr:
            return module_installed(
                environment=Environment(cr, odoo.SUPERUSER_ID, {}))
    except Exception:
        pass
    return {}

def module_boot(db=None):
    server_wide_modules = odoo.conf.server_wide_modules or ['web']
    serverside = []
    dbside = []
    for i in server_wide_modules:
        if i in http.addons_manifest:
            serverside.append(i)
    monodb = db or db_monodb()
    if monodb:
        dbside = module_installed_bypass_session(monodb)
        dbside = [i for i in dbside if i not in serverside]
    addons = serverside + dbside
    return addons

class V2Database(Database):

	def _render_template(self, **d):
		d.setdefault('manage',True)
		d['insecure'] = odoo.tools.config.verify_admin_password('admin')
		d['list_db'] = odoo.tools.config['list_db']
		d['langs'] = odoo.service.db.exp_list_lang()
		d['countries'] = odoo.service.db.exp_list_countries()
		d['pattern'] = DBNAME_PATTERN
		# databases list
		d['databases'] = []
		try:
			d['databases'] = http.db_list()
			d['incompatible_databases'] = odoo.service.db.list_db_incompatible(d['databases'])
		except odoo.exceptions.AccessDenied:
			monodb = db_monodb()
			if monodb:
				d['databases'] = [monodb]
		return env.get_template("database_manager.html").render(d)
		
	@http.route('/web/v2/selector', type='http', auth="none")
	def selector(self, **kw):
		request._cr = None
		return self._render_template(manage=False)

	@http.route('/web/v2/manager', type='http', auth="none")
	def manager(self, **kw):
		request._cr = None
		return self._render_template()

	@http.route('/web/v2/create', type='http', auth="none", methods=['POST'], csrf=False)
	def create(self, master_pwd, name, lang, password, **post):
		try:
			if not re.match(DBNAME_PATTERN, name):
				raise Exception(_('Invalid database name. Only alphanumerical characters, underscore, hyphen and dot are allowed.'))
			# country code could be = "False" which is actually True in python
			country_code = post.get('country_code') or False
			dispatch_rpc('db', 'create_database', [master_pwd, name, bool(post.get('demo')), lang, password, post['login'], country_code])
			request.session.authenticate(name, post['login'], password)
			return http.local_redirect('/web/')
		except Exception as e:
			error = "Database creation error: %s" % (str(e) or repr(e))
		return self._render_template(error=error)

	@http.route('/web/v2/duplicate', type='http', auth="none", methods=['POST'], csrf=False)
	def duplicate(self, master_pwd, name, new_name):
		try:
			if not re.match(DBNAME_PATTERN, new_name):
				raise Exception(_('Invalid database name. Only alphanumerical characters, underscore, hyphen and dot are allowed.'))
			dispatch_rpc('db', 'duplicate_database', [master_pwd, name, new_name])
			return http.local_redirect('/web/v2/manager')
		except Exception as e:
			error = "Database duplication error: %s" % (str(e) or repr(e))
			return self._render_template(error=error)

	@http.route('/web/v2/drop', type='http', auth="none", methods=['POST'], csrf=False)
	def drop(self, master_pwd, name):
		try:
			dispatch_rpc('db','drop', [master_pwd, name])
			request._cr = None  # dropping a database leads to an unusable cursor
			return http.local_redirect('/web/v2/manager')
		except Exception as e:
			error = "Database deletion error: %s" % (str(e) or repr(e))
			return self._render_template(error=error)

	@http.route('/web/v2/backup', type='http', auth="none", methods=['POST'], csrf=False)
	def backup(self, master_pwd, name, backup_format = 'zip'):
		try:
			odoo.service.db.check_super(master_pwd)
			ts = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
			filename = "%s_%s.%s" % (name, ts, backup_format)
			headers = [
				('Content-Type', 'application/octet-stream; charset=binary'),
				('Content-Disposition', content_disposition(filename)),
			]
			dump_stream = odoo.service.db.dump_db(name, None, backup_format)
			response = werkzeug.wrappers.Response(dump_stream, headers=headers, direct_passthrough=True)
			return response
		except Exception as e:
			_logger.exception('Database.backup')
			error = "Database backup error: %s" % (str(e) or repr(e))
			return self._render_template(error=error)

	@http.route('/web/v2/restore', type='http', auth="none", methods=['POST'], csrf=False)
	def restore(self, master_pwd, backup_file, name, copy=False):
		try:
			data_file = None
			db.check_super(master_pwd)
			with tempfile.NamedTemporaryFile(delete=False) as data_file:
				backup_file.save(data_file)
			db.restore_db(name, data_file.name, str2bool(copy))
			return http.local_redirect('/web/v2/manager')
		except Exception as e:
			error = "Database restore error: %s" % (str(e) or repr(e))
			return self._render_template(error=error)
		finally:
			if data_file:
				os.unlink(data_file.name)

	@http.route('/web/v2/change_password', type='http', auth="none", methods=['POST'], csrf=False)
	def change_password(self, master_pwd, master_pwd_new):
		try:
			dispatch_rpc('db', 'change_admin_password', [master_pwd, master_pwd_new])
			return http.local_redirect('/web/v2/manager')
		except Exception as e:
			error = "Master password update error: %s" % (str(e) or repr(e))
			return self._render_template(error=error)

	@http.route('/web/v2/list', type='json', auth='none')
	def list(self):
		"""
		Used by Mobile application for listing database
		:return: List of databases
		:rtype: list
		"""
		return http.db_list()