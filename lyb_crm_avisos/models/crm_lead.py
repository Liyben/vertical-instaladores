# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, SUPERUSER_ID
from lxml import etree

class CrmLead(models.Model):
	_inherit = 'crm.lead'

	#Subtipo para la oportunidad
	sub_type = fields.Selection([('notice', 'Aviso'), ('opportunity', 'Oportunidad')], index=True)

	#Etapa del crm
	stage_id = fields.Many2one(
		domain="[('team_id', 'in', [team_id, False]), "
			   "('crm_sub_type', 'in', [sub_type, 'both'])]")

	@api.model_create_multi
	def create(self, vals_list):
		# Creamos el aviso para cambiar los seguidores del documento
		record = super(CrmLead,self.with_context(mail_create_nosubscribe=True)).create(vals_list)

		#Asignamos la secuencia correcta 
		if (record.sub_type == 'notice'):
			record.sequence_code = self.env.ref(
					"lyb_crm_avisos.sequence_notice", raise_if_not_found=False
				).next_by_id()
		
		return record

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

