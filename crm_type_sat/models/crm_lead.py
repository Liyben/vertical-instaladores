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

    def action_schedule_meeting(self, smart_calendar=True):
        """
        Sobrescribimos la acción original para asegurarnos de que, 
        si el tipo es 'sat', se vincule correctamente al calendario.
        """
        self.ensure_one()
        # Llamamos al comportamiento base traspasando el parámetro nativo
        action = super(CrmLead, self).action_schedule_meeting(smart_calendar=smart_calendar)
        
        # Inyectamos el ID en el contexto de la acción si se trata de un SAT
        if self.type == 'sat':
            context = action.get('context', {})
            context.update({
                'search_default_opportunity_id': self.id,
                'default_opportunity_id': self.id,
            })
            action['context'] = context
            
        return action
    
    @api.depends('calendar_event_ids', 'calendar_event_ids.start')
    def _compute_meeting_display(self):
        # 1. Dejamos que Odoo procese el estándar (type == 'opportunity')
        super(CrmLead, self)._compute_meeting_display()
        
        # 2. Rescatamos nuestros registros SAT que el core ignora
        sat_leads = self.filtered(lambda lead: lead.type == 'sat')
        
        if sat_leads:
            # Buscamos las próximas reuniones para nuestros SATs
            meeting_data = self.env['calendar.event'].search_read([
                ('opportunity_id', 'in', sat_leads.ids),
                ('start', '>=', fields.Datetime.now())
            ], ['start', 'opportunity_id'], order='start')
            
            # Agrupamos quedándonos solo con la fecha más próxima (la primera que llega al estar ordenadas por 'start')
            next_events_dict = {}
            for meeting in meeting_data:
                lead_id = meeting['opportunity_id'][0]
                if lead_id not in next_events_dict:
                    next_events_dict[lead_id] = meeting['start']
                    
            # Asignamos las etiquetas y fechas a cada SAT
            for lead in sat_leads:
                start_date = next_events_dict.get(lead.id)
                if not start_date:
                    lead.meeting_display_label = _('No Meeting')
                    lead.meeting_display_date = False
                else:
                    date_start = start_date.date()
                    today = fields.Date.context_today(lead)
                    if date_start == today:
                        lead.meeting_display_label = _('Today')
                    elif date_start == today + timedelta(days=1):
                        lead.meeting_display_label = _('Tomorrow')
                    else:
                        lead.meeting_display_label = _('Next Meeting')
                    
                    lead.meeting_display_date = date_start