# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

class AccountMoveLine(models.Model):

    _inherit='account.move.line'

    
    #Campos relacionales para trabajos y materiales
    task_works_ids = fields.One2many(
        comodel_name='account.move.line.task.work', inverse_name='account_move_line_id', string='Trabajos', copy=True,
        store=True, readonly=False, precompute=True, compute='_compute_materials_and_works')
    task_materials_ids = fields.One2many(
        comodel_name='account.move.line.task.material', inverse_name='account_move_line_id', string='Materiales', copy=True,
        store=True, readonly=False, precompute=True, compute='_compute_materials_and_works')
    #Precio totales, unitarios y beneficio de Trabajos
    total_sp_work = fields.Float(string='Total P.V.', digits='Product Price', store=True, compute='_compute_total_sp_work')
    total_cp_work = fields.Float(string='Total P.C.', digits='Product Price', store=True, compute='_compute_total_cp_work')
    benefit_work = fields.Float(string='Beneficio (%)', digits='Product Price', compute='_compute_benefit_work')
    benefit_work_amount = fields.Float(string='Beneficio (€)', digits='Product Price', compute='_compute_benefit_work')
    total_hours = fields.Float(string='Total horas', compute='_compute_total_hours')
    #Precios totales, unitarios  y beneficio de Materiales
    total_sp_material = fields.Float(string='Total P.V.', digits='Product Price', store=True, compute='_compute_total_sp_material')
    total_cp_material = fields.Float(string='Total P.C.', digits='Product Price', store=True, compute='_compute_total_cp_material')
    benefit_material = fields.Float(string='Beneficio (%)', digits='Product Price', compute='_compute_benefit_material')
    benefit_material_amount = fields.Float(string='Beneficio (€)', digits='Product Price', compute='_compute_benefit_material')
    #Campo boolean para saber si crear o no una tarea de forma automatica
    auto_create_task = fields.Boolean(string='Tarea automática', related='product_id.auto_create_task', store=True)
    #Opciones de impresión por linea de pedido
    detailed_time = fields.Boolean(string='Imp. horas')
    detailed_price_time = fields.Boolean(string='Imp. precio Hr.')
    detailed_materials = fields.Boolean(string='Imp.materiales')
    detailed_price_materials = fields.Boolean(string='Imp. precio Mat.')
    detailed_subtotal_price_time = fields.Boolean(string='Imp. subtotal Hr.')
    detailed_subtotal_price_materials = fields.Boolean(string='Imp. subtotal Mat.')
    #Campo para controlar la visualización de los trabajos y materiales
    see_works_and_materials = fields.Selection([
        ('all', 'Trabajos y Materiales'),
        ('only_works', 'Solo Trabajos'),
        ('only_materials', 'Solo Materiales')],
        string="Ver", default='all')

    #Carga de los materiales y mano de obra
    @api.depends('product_id')
    def _compute_materials_and_works(self):
        for line in self:
            if line.product_id.type == 'service':
                self.see_works_and_materials = line.product_id.see_works_and_materials
            else:
                self.see_works_and_materials = False

            line.update({'task_works_ids' : False,
                        'task_materials_ids' : False,})
            
            if line.auto_create_task and self.see_works_and_materials != False:
                
                work_list = []
                if line.see_works_and_materials != 'only_materials':
                    for work in line.product_id.task_works_ids:
                        work_list.append((0,0, {
                            'name' : work.name,
                            'work_id': work.work_id.id,
                            'sale_price_unit' : work.sale_price_unit,
                            'cost_price_unit' : work.cost_price_unit,
                            'hours' : work.hours,
                            'discount' : work.discount
                            }))

                material_list = []
                if line.see_works_and_materials != 'only_works':
                    for material in line.product_id.task_materials_ids:
                        material_list.append((0,0, {
                            'material_id' : material.material_id.id,
                            'name' : material.name,
                            'sale_price_unit' : material.sale_price_unit,
                            'cost_price_unit' : material.cost_price_unit,
                            'quantity' : material.quantity,
                            'discount' : material.discount
                            }))

                line.update({'task_works_ids' : work_list,
                        'task_materials_ids' : material_list,})


    #Calculo del precio total de venta de los trabajos    
    @api.depends('task_works_ids', 'task_works_ids.sale_price')
    def _compute_total_sp_work(self):
        self.total_sp_work = 0.0
        for record in self:
            if record.task_works_ids:
                record.total_sp_work = sum(record.task_works_ids.mapped('sale_price'))

    #Calculo del precio total de coste de los trabajos    
    @api.depends('task_works_ids', 'task_works_ids.cost_price')
    def _compute_total_cp_work(self):
        self.total_cp_work = 0.0
        for record in self:
            if record.task_works_ids:
                record.total_cp_work = sum(record.task_works_ids.mapped('cost_price'))

    #Calculo del total de horas de los trabajos    
    @api.depends('task_works_ids', 'task_works_ids.hours')
    def _compute_total_hours(self):
        self.total_hours = 0.0
        for record in self:
            if record.task_works_ids:
                record.total_hours = sum(record.task_works_ids.mapped('hours'))

    #Calculo del beneficio de los trabajos    
    @api.depends('total_sp_work', 'total_cp_work')
    def _compute_benefit_work(self):
        self.benefit_work = 0.0
        self.benefit_work_amount = 0.0
        for record in self:
            record.benefit_work_amount = record.total_sp_work - record.total_cp_work
            if (record.total_sp_work != 0) and (record.total_cp_work != 0):
                record.benefit_work = (1-(record.total_cp_work/record.total_sp_work))
            
    #Calculo del precio total de venta de los materiales    
    @api.depends('task_materials_ids', 'task_materials_ids.sale_price')
    def _compute_total_sp_material(self):
        self.total_sp_material = 0.0
        for record in self:
            if record.task_materials_ids:
                record.total_sp_material = sum(record.task_materials_ids.mapped('sale_price'))

    #Calculo del precio total de coste de los materiales    
    @api.depends('task_materials_ids', 'task_materials_ids.cost_price')
    def _compute_total_cp_material(self):
        self.total_cp_material = 0.0
        for record in self:
            if record.task_materials_ids:
                record.total_cp_material = sum(record.task_materials_ids.mapped('cost_price'))

    #Calculo del beneficio de los materiales    
    @api.depends('total_sp_material', 'total_cp_material')
    def _compute_benefit_material(self):
        self.benefit_material = 0.0
        self.benefit_material_amount = 0.0
        for record in self:
            record.benefit_material_amount = record.total_sp_material - record.total_cp_material
            if (record.total_cp_material != 0) and (record.total_sp_material != 0):
                record.benefit_material = (1-(record.total_cp_material/record.total_sp_material))

    #Activa la función para calcular el precio unitario tambien cuando se cambia los materiales y mano de obra
    @api.depends('task_works_ids', 'task_materials_ids', 'task_works_ids.sale_price', 'task_materials_ids.sale_price')
    def _compute_price_unit(self):
        super()._compute_price_unit()
        for line in self:
            if line.task_works_ids or line.task_materials_ids:
                line.price_unit = (line.total_sp_material + line.total_sp_work)
                #line.purchase_price = (line.total_cp_material + line.total_cp_work)
        return True

    #Abre la linea de factura en un formulario en primer plano
    def action_invoice_line_open(self):
        invoice_line_form = self.env.ref('product_task_material_work.view_invoice_line_form', False)
        return {
                'type': 'ir.actions.act_window',
                'name': _('Linea de factura'),
                'res_model': 'account.move.line',
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(invoice_line_form.id, 'form')],
                'view_id': invoice_line_form.id,
                'target': 'current',}


