# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models

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

	@api.multi
	def btn_reset_domain(self):
		for line in self:
			line.analytic_account_id = False
			for query in line.query_ids:
				query.domain = ""