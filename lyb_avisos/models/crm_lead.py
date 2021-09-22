# © 2021 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, SUPERUSER_ID


class CrmLead(models.Model):
	_inherit = 'crm.lead'

	#def _default_stage_id(self):
	#    if (self.sub_type and self.sub_type == 'notice'):
	#        team = self.env.ref('lyb_avisos.crm_canal_aviso', raise_if_not_found=False)
	#    else:
	#        team = self.env['crm.team'].sudo()._get_default_team_id(user_id=self.env.uid)
	#        
	#    return self._stage_find(team_id=team.id, domain=[('fold', '=', False)]).id


	#Campos necesarios para el uso de CRM como AVISOS
	date_begin = fields.Datetime(string='Visitar el', default=fields.Datetime.now)
	date_end = fields.Datetime(string='Fecha fin')
	next_action = fields.Char(string='Acción siguiente')
	date_creation = fields.Datetime(string='Fecha creación', default=fields.Datetime.now, readonly=True, store=True)

	note = fields.Html(string='Descripción')

	#Campos necesarios para la secuencia
	sequence_code = fields.Char(string='Nº serie', default="/", required=True, readonly=True, copy=False)
	_sql_constraints = [
		("crm_lead_unique_sequence_code", "UNIQUE (sequence_code)", _("La secuencia debe ser única!!")),
		]

	#Tracking para el campo Oficial 1
	worker_one = fields.Many2one('res.users', string='Oficial 1', track_visibility='onchange')
	worker_two = fields.Many2one('res.users', string='Oficial 2')
	helpers = fields.Char(string='Ayudante/s')

	#Solo se usa en la migración de datos para guardar de forma temporal el id de la antigua BBDD
	old_id = fields.Integer(string="Id antiguo")

	#Subtipo para la oportunidad
	sub_type = fields.Selection([('notice', 'Aviso'), ('opportunity', 'Oportunidad')], index=True)

	sub_team_id = fields.Many2one('crm.team', string='Team', ondelete='set null')

	#Etapa del crm
	stage_id = fields.Many2one(
		domain="[('team_id', 'in', [team_id, False]), "
			   "('crm_sub_type', 'in', [sub_type, 'both'])]")
			   
	#Calendariza el aviso con el oficial de 1ª
	def action_schedule_workers(self):

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
		action['context'] = {
			'default_opportunity_id': self.id if self.type == 'opportunity' else False,
			'default_partner_id': self.partner_id.id,
			'default_partner_ids': partner_ids,
			'default_attendee_ids': [(0, 0, {'partner_id': pid}) for pid in partner_ids],
			'default_team_id': self.team_id.id,
			'default_name': self.name,
		}
		return action

	@api.model_create_multi
	def create(self, vals_list):
		# Creamos el aviso para cambiar los seguidores del documento
		record = super(CrmLead,self.with_context(mail_create_nosubscribe=True)).create(vals_list)

		#Asignamos la secuencia correcta 
		if (record.sub_type == 'notice'):
			record.sequence_code = self.env.ref(
					"lyb_avisos.sequence_notice", raise_if_not_found=False
				).next_by_id()
		elif (record.sub_type == 'opportunity'):
			record.sequence_code = self.env.ref(
					"lyb_avisos.sequence_opportunity", raise_if_not_found=False
				).next_by_id()

		#Lista de seguidores
		follower_ids = []

		#Añadimos el trabajador a la lista de seguidores
		if record.worker_one:
			follower_ids.append(record.worker_one.id)

		#Añadimos la lista de seguidores al aviso
		if follower_ids:
			record.message_subscribe_users(user_ids= follower_ids)

		#Mandamos el correo a los seguidores del aviso con los datos de este. También se envia otro correo al comercial
		message = _("<p>Estimado/a %s,</p> <p>Ha sido asignado/a al aviso %s.</p>") % (record.worker_one.name, record.name)
		subject = _("%s : %s") % (record.sequence_code, record.name)
		record.message_post(body=message, message_type='comment', subtype_xmlid='mail.mt_comment', subject=subject, author_id=record.user_id.partner_id.id)

		return record

	def write(self,vals):

		follower_ids = []

		old_worker_id = 0

		#Descubribimos el trabajor de la lista de seguidores y guardamos su id
		if self.worker_one:
			follower_ids.append(self.worker_one.id)
			old_worker_id = self.worker_one.partner_id.id
			self.message_unsubscribe(partner_ids=follower_ids)
			follower_ids = []

		#Suscribimos el trabajor al aviso y le mandamos el correo si hay cambio de oficial
		if vals.get('worker_one'):
			worker = self.env['res.users'].browse(vals.get('worker_one'))
			follower_ids.append(worker.partner_id.id)
			self.message_subscribe(partner_ids=follower_ids)

			if old_worker_id != worker.id:
				message = _("<p>Estimado/a %s,</p> <p>Ha sido asignado/a al aviso %s.</p>") % (worker.name, self.name)
				subject = _("%s : %s") % (self.sequence_code, self.name)
				self.message_post(body=message, message_type='comment', subtype_xmlid='mail.mt_comment', subject=subject, author_id=self.user_id.partner_id.id)

		return super(CrmLead,self.with_context(mail_create_nosubscribe=True)).write(vals)

	@api.returns('self', lambda value: value.id)
	def copy(self, default=None):
		if default is None:
			default = {}
			
		#Ponemos el dia actual por defecto en la fecha de creacion
		default['date_creation'] = fields.Datetime.now()
			
		return super(CrmLead,self).copy(default=default)

	#Funciones redefinidas para el uso del subtipo en las etapas
	@api.model
	def _read_group_stage_ids(self, stages, domain, order):
		ctx_type = self.env.context.get('default_sub_type')
		stages = super(CrmLead, self)._read_group_stage_ids(stages, domain, order)
		search_domain = [('id', 'in', stages.ids)]
		if ctx_type:
			search_domain += [('crm_sub_type', 'in', [ctx_type, 'both'])]
		stage_ids = stages._search(
			search_domain, order=order, access_rights_uid=SUPERUSER_ID)
		return stages.browse(stage_ids)

	def _stage_find(self, team_id=False, domain=None, order='sequence'):
		# check whether we should try to add a condition on type
		domain = domain or []
		if not any(
			[term for term in domain if len(term) == 3 and term[0] == "crm_sub_type"]
		):
			types = ["both"]
			ctx_type = self.env.context.get("default_sub_type")
			if ctx_type:
				types += [ctx_type]
			domain.append(("crm_sub_type", "in", types))
		return super(CrmLead, self)._stage_find(team_id, domain, order)

	def merge_opportunity(self, user_id=False, team_id=False, auto_unlink=True):
		opportunities_head = super(CrmLead, self).merge_opportunity(
			user_id, team_id,auto_unlink)
		if opportunities_head.team_id:
			team_stage_ids = self.env['crm.stage'].search(
				[('team_id', 'in', [opportunities_head.team_id.id, False]),
				 ('crm_sub_type', 'in', [opportunities_head.sub_type, 'both'])],
				order='sequence')
			if opportunities_head.stage_id not in team_stage_ids:
				opportunities_head.write({
					'stage_id': team_stage_ids[0] if team_stage_ids else False
				})
		return opportunities_head

	def _convert_opportunity_data(self, customer, team_id=False):
		value = super(CrmLead, self)._convert_opportunity_data(customer, team_id)
		if not self.stage_id or self.stage_id.crm_sub_type == 'notice':
			stage = self._stage_find(
				team_id=team_id, domain=[('crm_sub_type', 'in',
										  ['opportunity', 'both'])])
			value['stage_id'] = stage.id
		return value