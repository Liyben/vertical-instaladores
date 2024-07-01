# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models

from odoo.addons.mis_builder.models.expression_evaluator import ExpressionEvaluator
from odoo.addons.mis_builder.models.mis_safe_eval import NameDataError, mis_safe_eval

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

class MisReportInstance(models.Model):
	_inherit = 'mis.report.instance'

	def btn_set_domain(self):
		for line in self:
			line.report_id.btn_set_domain(line.analytic_account_id.id)

	def btn_reset_domain(self):
		for line in self:
			line.analytic_account_id = False
			line.report_id.btn_reset_domain()

class MisBuilderLiybenExpressionEvaluator(ExpressionEvaluator):
	def eval_expressions(self, expressions, locals_dict):
		vals = []
		drilldown_args = []
		name_error = False
		for expression in expressions:
			expr = expression and expression.name or "AccountingNone"
			if self.aep:
				replaced_expr = self.aep.replace_expr(expr)
			else:
				replaced_expr = expr
			val = mis_safe_eval(replaced_expr, locals_dict)
			_logger.debug("eval expressions: %s/n",str(val))
			vals.append(val)
			if isinstance(val, NameDataError):
				name_error = True
			if replaced_expr != expr:
				drilldown_args.append({"expr": expr})
			else:
				drilldown_args.append(None)
		return vals, drilldown_args, name_error

	def eval_expressions_by_account(self, expressions, locals_dict):
		if not self.aep:
			return
		exprs = [e and e.name or "AccountingNone" for e in expressions]
		for account_id, replaced_exprs in self.aep.replace_exprs_by_account_id(exprs):
			vals = []
			drilldown_args = []
			name_error = False
			for expr, replaced_expr in zip(exprs, replaced_exprs):
				val = mis_safe_eval(replaced_expr, locals_dict)
				_logger.debug("eval expressions by account: %s/n",str(val))
				vals.append(val)
				if replaced_expr != expr:
					drilldown_args.append({"expr": expr, "account_id": account_id})
				else:
					drilldown_args.append(None)
			yield account_id, vals, drilldown_args, name_error 