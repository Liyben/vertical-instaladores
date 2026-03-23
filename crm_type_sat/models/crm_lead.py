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

    # Relación Padre-Hijo para SAT
    parent_id = fields.Many2one(
        'crm.lead', 
        string='SAT Padre', 
        index=True, 
        ondelete='cascade',
        domain="[('type', '=', 'sat'), ('id', '!=', id)]"
    )
    child_ids = fields.One2many(
        'crm.lead', 
        'parent_id', 
        string='Sub-Avisos (Hijos)'
    )
    child_sat_count = fields.Integer(
        string='Número de Sub-Avisos',
        compute='_compute_child_sat_count'
    )

    #Etapa del crm
    stage_id = fields.Many2one(
        domain="[('team_id', 'in', [team_id, False]), "
               "('type', 'in', [type, 'both'])]")

    @api.depends('child_ids')
    def _compute_child_sat_count(self):
        for lead in self:
            lead.child_sat_count = len(lead.child_ids)

    def action_view_child_sats(self):
        """Devuelve la acción para abrir la vista de los sub-avisos (hijos)"""
        self.ensure_one()
        return {
            'name': _('Sub-Avisos'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,kanban,form,calendar',
            'res_model': 'crm.lead',
            'domain': [('parent_id', '=', self.id)],
            'context': {
                'default_type': 'sat',
                'default_parent_id': self.id,
            },
        }
    
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

