# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    #Campo para relacionar Aviso / Oportunidad con PT
    task_ids = fields.One2many(comodel_name='project.task', inverse_name='oppor_id', string="Partes de Trabajo")
    
    #Campo para el plan analitico
    plan_id = fields.Many2one(
        'account.analytic.plan',
        string='Plan analítico',
    )

    #Calculo del contexto cuando una oportunidad pasa a presupuesto
    def _prepare_opportunity_quotation_context(self):
        """Generate context values"""
        quotation_context = super()._prepare_opportunity_quotation_context()
        if self.plan_id:
            quotation_context['default_plan_id'] = self.plan_id.id
        if self.project_id:
            quotation_context['default_visible_project'] = True
            quotation_context['default_project_id'] = self.project_id.id
        return quotation_context