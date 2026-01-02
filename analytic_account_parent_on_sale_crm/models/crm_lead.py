# © 2025 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    #Cuenta analítica madre
    analytic_account_parent_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Cuenta analítica madre",
        copy=False, check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    @api.onchange('team_id')
    def _onchange_team_id_to_analytic_account_parent_id(self):
        for record in self:
            if record.team_id and record.team_id.analytic_account_parent_id:
                record.analytic_account_parent_id = record.team_id.analytic_account_parent_id.id
            else:
                record.analytic_account_parent_id = False

    #Calculo del contexto cuando una oportunidad pasa a presupuesto
    def _prepare_opportunity_quotation_context(self):
        """Generate context values"""
        quotation_context = super()._prepare_opportunity_quotation_context()
        if self.analytic_account_parent_id:
            quotation_context['default_analytic_account_parent_id'] = self.analytic_account_parent_id.id
        if self.project_id:
            quotation_context['default_visible_project'] = True
            quotation_context['default_project_id'] = self.project_id.id
        return quotation_context