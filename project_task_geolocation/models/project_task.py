# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime
from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp

UNIT = dp.get_precision("Geolocalizacion")

class ProjectTaskTimeSheet(models.Model):
    _inherit = 'account.analytic.line'

    date_start = fields.Datetime(string='Inicio')
    date_end = fields.Datetime(string='Fin', readonly=1)
    timer_duration = fields.Float(invisible=1, string='Duración')
    check_in_url_map = fields.Char(string="Localización de inicio",readonly=1)
    check_out_url_map = fields.Char(string="Localización de fin",readonly=1)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    latitude = fields.Float(
        "Check-in Latitude",
        digits=UNIT,
        readonly=True
    )
    longitude = fields.Float(
        "Check-in longitude",
        digits=UNIT,
        readonly=True
    )
    check_in_url_map = fields.Char(string="Localización",readonly=1)
    geolocation_task = fields.Boolean()
    is_user_working = fields.Boolean(
        'Is Current User Working', compute='_compute_is_user_working',
        help="Technical field indicating whether the current user is working. ")

    def _compute_is_user_working(self):
        """ Checks whether the current user is working """
        for order in self:
            if order.timesheet_ids.filtered(lambda x: (x.user_id.id == self.env.user.id) and (not x.date_end)):
                order.is_user_working = True
            else:
                order.is_user_working = False
    
    @api.multi
    def manual_geolocation(self, location=False):
        if (location):
            self.latitude = location[0]
            self.longitude = location[1]


    """ @api.multi
    def toggle_start(self):
        location = ""        
        for record in self:
            record.geolocation_task = not record.geolocation_task
            if record.latitude!=0.0 and record.longitude!=0.0:
                location = "https://maps.google.com/?q=%f,%f" % (record.latitude,record.longitude)

        if self.geolocation_task:
            self.write({'is_user_working': True})
            time_line = self.env['account.analytic.line']
            for time_sheet in self:
                time_line.create({
                    'name': self.env.user.name + ': ' + time_sheet.name,
                    'task_id': time_sheet.id,
                    'user_id': self.env.user.id,
                    'project_id': time_sheet.project_id.id,
                    'date_start': datetime.now(),
                    'check_in_url_map': location,
                })
        else:
            self.write({'is_user_working': False})
            time_line_obj = self.env['account.analytic.line']
            domain = [('task_id', 'in', self.ids), ('date_end', '=', False)]
            for time_line in time_line_obj.search(domain):
                time_line.write({
                    'date_end': fields.Datetime.now(),
                    'check_out_url_map': location,
                })
                if time_line.date_end:
                    diff = fields.Datetime.from_string(time_line.date_end) - fields.Datetime.from_string(time_line.date_start)
                    time_line.timer_duration = round(diff.total_seconds() / 60.0, 2)
                    time_line.unit_amount = round(diff.total_seconds() / (60.0 * 60.0), 2)
                else:
                    time_line.unit_amount = 0.0
                    time_line.timer_duration = 0.0
        
        return {
            'name' : 'Ubicación',
            'type' : 'ir.actions.act_url',
            'target': 'new',
            'url' : location
        } """

    @api.multi
    def toggle_start(self):
        location = ""        
        if self.latitude!=0.0 and self.longitude!=0.0:
            location = "https://maps.google.com/?q=%f,%f" % (self.latitude,self.longitude)

        time_line_obj = self.env['account.analytic.line']
        domain = [('task_id', 'in', self.ids), ('date_end', '=', False), ('user_id', '=', self.env.user.id)]
        time_line_ids = time_line_obj.search(domain)
        if time_line_ids:
            self.write({'is_user_working': False})
            for time_line in time_line_ids:
                time_line.write({
                    'date_end': fields.Datetime.now(),
                    'check_out_url_map': location,
                })
                if time_line.date_end:
                    diff = fields.Datetime.from_string(time_line.date_end) - fields.Datetime.from_string(time_line.date_start)
                    time_line.timer_duration = round(diff.total_seconds() / 60.0, 2)
                    time_line.unit_amount = round(diff.total_seconds() / (60.0 * 60.0), 2)
                else:
                    time_line.unit_amount = 0.0
                    time_line.timer_duration = 0.0
        else:
            self.write({'is_user_working': True})
            for time_sheet in self:
                time_line_obj.create({
                    'name': self.env.user.name + ': ' + time_sheet.name,
                    'task_id': time_sheet.id,
                    'user_id': self.env.user.id,
                    'project_id': time_sheet.project_id.id,
                    'date_start': datetime.now(),
                    'check_in_url_map': location,
                })
        
        return {
            'name' : 'Ubicación',
            'type' : 'ir.actions.act_url',
            'target': 'new',
            'url' : location
        }