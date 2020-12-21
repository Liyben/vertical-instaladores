# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ProjectTaskMergeWizard(models.TransientModel):
    _inherit = 'project.task.merge.wizard'
    
    
    #Combina los parte de horas de los PTs seleccionados
    @api.multi
    def merge_timesheet(self):
        timesheet_list = []
        for task in self.task_ids:
            if task.timesheet_ids:
                for timesheet in task.timesheet_ids:
                    timesheet_list.append((0,0, {
                        'date' : timesheet.date,
                        'name' : timesheet.name,
                        'employee_id' : timesheet.employee_id.id,
                        'unit_amount' : timesheet.unit_amount,
                        'account_id' : timesheet.account_id.id,
                        'date_start' : timesheet.date_start,
                        'date_end' : timesheet.date_end,
                        'timer_duration' : timesheet.timer_duration,
                        'check_in_url_map' : timesheet.check_in_url_map,
                        'check_out_url_map' : timesheet.check_out_url_map
                        }))

        if timesheet_list == []:
            timesheet_list = False

        return timesheet_list
