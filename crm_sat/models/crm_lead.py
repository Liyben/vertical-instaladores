# © 2024 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    _rec_names_search = ["name", "sequence_code"]

    @api.depends('tag_ids')
    def _compute_has_tags(self):
        for record in self:
            record.has_tags = bool(record.tag_ids)

    #Campo boolean para saber si hay o no etiquetas
    has_tags = fields.Boolean(compute="_compute_has_tags")

    date_creation = fields.Datetime(string='Fecha creación', default=fields.Datetime.now, readonly=True, store=True)

    #Campos necesarios para la secuencia
    sequence_code = fields.Char(string='Nº serie', default="/", required=True, readonly=True, copy=False)
    _sql_constraints = [
        ("crm_lead_unique_sequence_code", "UNIQUE (sequence_code)", _("La secuencia debe ser única!!")),
        ]

    #Tracking para el campo Oficial 1
    worker_one = fields.Many2one(
        'res.users', string='Oficial 1', 
        domain="[('share', '=', False)]",
        check_company=True, index=True, tracking=True)
    
    helpers = fields.Char(string='Ayudante/s')

    #Dirección de entrega
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Dirección de entrega",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False, precompute=True,
        check_company=True,
        index='btree_not_null')
    
    #Carga la direccioń de entrega al cambiar el cliente
    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        for record in self:
            record.partner_shipping_id = record.partner_id.address_get(['delivery'])['delivery'] if record.partner_id else False

    #Calendariza el aviso con el oficial de 1ª
    def action_schedule_meeting(self, smart_calendar=True):

        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")
        #Lista de Asistentes
        #Añadimos el usuario conectado
        partner_ids = self.env.user.partner_id.ids
        #Añadimos el cliente
        if self.partner_id:
            partner_ids.append(self.partner_id.id)
        #Añadimos el oficial de primera
        if self.worker_one:
            partner_ids.append(self.worker_one.partner_id.id)
        current_opportunity_id = self.id if self.type == 'opportunity' else False
        action['context'] = {
            'search_default_opportunity_id': current_opportunity_id,
            'default_opportunity_id': current_opportunity_id,
            'default_partner_id': self.partner_id.id,
            'default_partner_ids': partner_ids,
            'default_attendee_ids': [(0, 0, {'partner_id': pid}) for pid in partner_ids],
            'default_team_id': self.team_id.id,
            'default_name': self.name,
        }
        if current_opportunity_id and smart_calendar:
            mode, initial_date = self._get_opportunity_meeting_view_parameters()
            action['context'].update({'default_mode': mode, 'initial_date': initial_date})
        return action

    @api.model_create_multi
    def create(self, vals_list):

        #Asignamos la secuencia correcta 
        for vals in vals_list:
            if (vals.get("sequence_code", "/") == "/" and vals.get("type") == 'lead'):
                vals["sequence_code"] = self.env.ref(
                        "crm_sat.sequence_lead", raise_if_not_found=False
                    ).next_by_id()
                
            if (vals.get("sequence_code", "/") == "/" and vals.get("type") == 'opportunity'):
                vals["sequence_code"] = self.env.ref(
                        "crm_sat.sequence_opportunity", raise_if_not_found=False
                    ).next_by_id()

        return super().create(vals_list)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
            
        #Ponemos el dia actual por defecto en la fecha de creacion
        default['date_creation'] = fields.Datetime.now()
            
        return super(CrmLead,self).copy(default=default)

    def _convert_opportunity_data(self, customer, team_id=False):
        res = super(CrmLead,self)._convert_opportunity_data(customer, team_id)
        
        if res:
            res['sequence_code'] = self.env.ref(
                        "crm_sat.sequence_opportunity", raise_if_not_found=False
                    ).next_by_id()

        return res
    
    # ---------------------------------------------------------
    # UX: VISUALIZACIÓN EN LOS DESPLEGABLES MANY2ONE
    # ---------------------------------------------------------
    @api.depends('name', 'sequence_code')
    def _compute_display_name(self):
        """
        Garantiza que el usuario vea el código que acaba de buscar en el listado.
        Ejemplo: "[AV-001] Aviso de instalación"
        """
        for lead in self:
            if lead.sequence_code and lead.sequence_code != '/':
                lead.display_name = f"[{lead.sequence_code}] {lead.name}"
            else:
                lead.display_name = lead.name or ''