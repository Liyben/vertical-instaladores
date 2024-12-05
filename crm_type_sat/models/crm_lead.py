# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, SUPERUSER_ID
from lxml import etree

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    #tipo para sat
    type = fields.Selection(selection_add=[
        ('sat', 'SAT')
    ], ondelete={
        'sat': 'set default',
    })

    #Etapa del crm
    stage_id = fields.Many2one(
        domain="[('team_id', 'in', [team_id, False]), "
               "('type', 'in', [type, 'both'])]")

    @api.model_create_multi
    def create(self, vals_list):
        #Asignamos la secuencia correcta 
        for vals in vals_list:
            if (vals.get("sequence_code", "/") == "/" and vals.get("type") == 'sat'):
                vals["sequence_code"] = self.env.ref(
                        "crm_type_sat.sequence_sat", raise_if_not_found=False
                    ).next_by_id()
        
        return super().create(vals_list)

    #Funciones redefinidas para el uso del tipo en las etapas
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        type = self._context.get('default_type')
        stages = super(CrmLead, self)._read_group_stage_ids(stages, domain, order)
        search_domain = [('id', 'in', stages.ids)]
        if type:
            search_domain += [('type', 'in', [type, 'both'])]
        stage_ids = stages._search(
            search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def _stage_find(self, team_id=False, domain=None, order='sequence'):
        # check whether we should try to add a condition on type
        domain = domain or []
        if not any(
            [term for term in domain if len(term) == 3 and term[0] == "type"]
        ):
            types = ["both"]
            type = self._context.get('default_type')
            if type:
                types += [type]
            domain.append(("type", "in", types))
        return super(CrmLead, self)._stage_find(team_id, domain, order)

    def _convert_opportunity_data(self, customer, team_id=False):
        res = super(CrmLead,self)._convert_opportunity_data(customer, team_id)
        
        if res:
            res['sequence_code'] = self.env.ref(
                        "crm_type_sat.sequence_sat", raise_if_not_found=False
                    ).next_by_id()

        return res

