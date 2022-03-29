# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def write(self, vals):
        if 'stage_id' in vals:
            stage_id = self.env['crm.stage'].browse(vals['stage_id'])
            if stage_id.activity_type_id:
                activity = stage_id.activity_type_id
                xml_id = activity.get_external_id()
                for lead in self:
                    lead.activity_schedule(
                        xml_id.get(activity.id),
                        note=activity.default_description,
                        user_id=activity.default_user_id.id or self.env.user.id,
                    )

        return super().write(vals)