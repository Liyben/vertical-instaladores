# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, SUPERUSER_ID
from lxml import etree


class CrmLead(models.Model):
	_inherit = 'crm.lead'

	@api.depends('tag_ids')
	def _compute_has_tags(self):
		for record in self:
			record.has_tags = bool(record.tag_ids)

	#Campo boolean para saber si hay o no etiquetas
	has_tags = fields.Boolean(compute="_compute_has_tags")

	date_creation = fields.Datetime(string='Fecha creación', default=fields.Datetime.now, readonly=True, store=True)

	note = fields.Html(string='Descripción')

	#Campos necesarios para la secuencia
	sequence_code = fields.Char(string='Nº serie', default="/", required=True, readonly=True, copy=False)
	_sql_constraints = [
		("crm_lead_unique_sequence_code", "UNIQUE (sequence_code)", _("La secuencia debe ser única!!")),
		]

	#Tracking para el campo Oficial 1
	worker_one = fields.Many2one('res.users', string='Oficial 1', track_visibility='onchange')
	helpers = fields.Char(string='Ayudante/s')

	#Subtipo para la oportunidad
	sub_type = fields.Selection([('opportunity', 'Oportunidad')], index=True)

	#Dirección de entrega
	partner_shipping_id = fields.Many2one(
		'res.partner', string='Dirección de entrega', domain="[('parent_id', '=', partner_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

	#Cada vez qeu se produce un cambio en las etiquetas se pone vacio el equipo de ventas
	@api.onchange('tag_ids')
	def _onchange_tag_ids_to_false_team_id(self):
		for record in self:
			record.team_id = False

	#Calendariza el aviso con el oficial de 1ª
	def action_schedule_meeting(self):

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

		#Asignamos la secuencia correcta 
		for vals in vals_list:
			if (vals.get("sequence_code", "/") == "/" and vals.get("sub_type") == 'opportunity'):
				vals["sequence_code"] = self.env.ref(
						"lyb_crm_sat.sequence_opportunity", raise_if_not_found=False
					).next_by_id()

		# Creamos el aviso para cambiar los seguidores del documento
		record = super(CrmLead,self.with_context(mail_create_nosubscribe=True)).create(vals_list)

		#Lista de seguidores
		follower_ids = []

		#Añadimos el trabajador a la lista de seguidores
		if record.worker_one:
			follower_ids.append(record.worker_one.id)

		#Añadimos la lista de seguidores al aviso
		if follower_ids:
			record.message_subscribe(partner_ids=follower_ids)

		#Mandamos el correo a los seguidores del aviso con los datos de este. También se envia otro correo al comercial
		if record.worker_one:
			message = _("<p>Estimado/a %s,</p> <p>Ha sido asignado/a al aviso %s.</p>") % (record.worker_one.name, record.name)
			subject = _("%s : %s") % (record.sequence_code, record.name)
			record.message_post(body=message, message_type='comment', subtype_xmlid='mail.mt_comment', subject=subject, author_id=record.user_id.partner_id.id)

		return record

	def write(self,vals):

		follower_ids = []

		old_worker_id = 0

		#Desuscribimos el trabajor de la lista de seguidores y guardamos su id
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

	#Añade el subtipo oportunidad
	def _convert_opportunity_data(self, customer, team_id=False):
		res = super(CrmLead,self)._convert_opportunity_data(customer, team_id)
		
		if res:
			res['sub_type'] = 'opportunity'
			res['sequence_code'] = self.env.ref(
						"lyb_crm_sat.sequence_opportunity", raise_if_not_found=False
					).next_by_id()

		return res