# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)

class MisReportQuery(models.Model):

	_inherit = 'mis.report.query'

	base_domain = fields.Char(string="Dominio base")
	name_analytic_account = fields.Char(string="N. campo cta. analítica")

class MisReport(models.Model):

	_inherit = 'mis.report'

	analytic_account_id = fields.Many2one(comodel_name="account.analytic.account", string="Cuenta analítica",)
	active = fields.Boolean(default=True)

	@api.onchange("analytic_account_id")
	def _onchange_analytic_account_id(self):
		
		if self.analytic_account_id:
			aacc_id = self.analytic_account_id.id

			for line in self:
				if line.query_ids:
					for query in line.query_ids:
						res=""
						if query.base_domain and query.name_analytic_account:
							res = "[" + query.base_domain + ", ('" + query.name_analytic_account + "', '=', " + str(aacc_id) +")]"
						elif query.base_domain:
							res = "[" + query.base_domain + "]"
						elif query.name_analytic_account:
							res = "[('" + query.name_analytic_account + "', '=', " + str(aacc_id) +")]"

						query.domain = res

	
	def btn_reset_domain(self):
		for line in self:
			line.analytic_account_id = False
			for query in line.query_ids:
				query.domain = ""


	def btn_set_domain(self, analytic_account):
		for line in self:
			for query in line.query_ids:
				res=""
				if query.base_domain and query.name_analytic_account:
					res = "[" + query.base_domain + ", ('" + query.name_analytic_account + "', '=', " + str(analytic_account) +")]"
				elif query.base_domain:
					res = "[" + query.base_domain + "]"
				elif query.name_analytic_account:
					res = "[('" + query.name_analytic_account + "', '=', " + str(analytic_account) +")]"

				query.domain = res

	def _fetch_queries(self, date_from, date_to, get_additional_query_filter=None):
		res = super(MisReport, self)._fetch_queries(date_from, date_to, get_additional_query_filter)
		_logger.debug("%s\n", str(res.values()))
		return res

class MisReportInstance(models.Model):
	_inherit = 'mis.report.instance'

	def btn_set_domain(self):
		for line in self:
			line.report_id.btn_set_domain(line.analytic_account_id.id)

	def btn_reset_domain(self):
		for line in self:
			line.analytic_account_id = False
			line.report_id.btn_reset_domain()