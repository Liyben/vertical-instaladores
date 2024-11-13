# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    
    _inherit='sale.order'

    #Precio totales, unitarios y beneficio de Trabajos segun presupuesto
    total_sp_work = fields.Float(string='P.V. Total', digits='Product Price', compute='_compute_price_work', store=True)
    total_cp_work = fields.Float(string='P.C. Total', digits='Product Price', compute='_compute_price_work', store=True)
    sale_price_work_hour = fields.Float(string='P.V. Hora', digits='Product Price', compute="_compute_price_work", store=True)
    cost_price_work_hour = fields.Float(string='P.C. Hora', digits='Product Price', compute="_compute_price_work", store=True)
    benefit_work = fields.Float(string='Beneficio', digits='Product Price', compute='_compute_price_work', store=True)
    total_hours = fields.Float(string='Total horas', compute='_compute_price_work', store=True)

    #Precio totales, unitarios y beneficio de Trabajos real
    total_sp_real_work = fields.Float(string='P.V. Total', digits='Product Price', related='total_sp_work', store=True)
    total_cp_real_work = fields.Float(string='P.C. Total', digits='Product Price', compute='_compute_price_work_real', store=True)
    sale_price_real_work_hour = fields.Float(string='P.V. Hora', digits='Product Price', store=True, related='sale_price_work_hour')
    cost_price_real_work_hour = fields.Float(string='P.C. Hora', digits='Product Price')
    benefit_real_work = fields.Float(string='Beneficio', digits='Product Price', compute='_compute_price_work_real', store=True)
    total_real_hours = fields.Float(string='Total horas')
    
    #Margenes y descuento de los totales
    discount_general = fields.Float(string='Descuento', digits='Discount')
    margin_order_monetary = fields.Float(string='Margen Ppto', digits='Product Price', compute='_compute_sale_order', store=True)
    margin_order_percent = fields.Float(string='Margen Ppto', digits='Product Price', compute='_compute_sale_order', store=True)
    margin_real_monetary = fields.Float(string='Margen Real', digits='Product Price', compute='_compute_real', store=True)
    margin_real_percent = fields.Float(string='Margen Real', digits='Product Price', compute='_compute_real', store=True) 

    #Precios totales y beneficio de Materiales Presupuesto
    total_sp_material = fields.Float(string='P.V. Total', digits='Product Price', compute='_compute_price_material', store=True)
    total_cp_material = fields.Float(string='P.C. Total', digits='Product Price', compute='_compute_price_material', store=True)
    benefit_material = fields.Float(string='Beneficio', digits='Product Price', compute='_compute_price_material', store=True)

    #Precios totales y beneficio de Materiales Reales
    total_sp_real_material = fields.Float(string='P.V. Total', digits='Product Price', related='total_sp_material', store=True)
    total_cp_real_material = fields.Float(string='P.C. Total', digits='Product Price')
    benefit_real_material = fields.Float(string='Beneficio', digits='Product Price', compute='_compute_price_material_real', store=True)

    #Calculo del precio de venta y coste de los trabajos y su beneficio segun presupuesto    
    @api.depends('order_line', 'order_line.total_sp_work', 'order_line.total_cp_work', 'order_line.product_uom_qty', 'order_line.discount', 'order_line.total_hours')
    def _compute_price_work(self):
        sale = 0.0
        cost = 0.0
        hours = 0.0        
        for order in self:
            order.sale_price_work_hour = 0.0
            order.cost_price_work_hour = 0.0
            order.benefit_work = 0.0
            for line in order.order_line:
                if line.product_id.type == 'service':
                    if line.auto_create_task:
                        if line.see_works_and_materials != 'only_materials':
                            sale = sale + (line.total_sp_work * line.product_uom_qty * (1 - (line.discount/100)))
                            cost = cost + (line.total_cp_work * line.product_uom_qty)
                            hours = hours + (line.total_hours * line.product_uom_qty)
                    else:
                        sale = sale + ((line.price_unit * line.product_uom_qty) * (1 - (line.discount/100)))
                        cost = cost + (line.purchase_price * line.product_uom_qty)
                        hours = hours + line.product_uom_qty
            order.total_sp_work = sale
            order.total_cp_work = cost
            order.total_hours = hours
            if (hours != 0):
                order.sale_price_work_hour = sale/hours
                order.cost_price_work_hour = cost/hours
            if (cost != 0) and (sale != 0):
                order.benefit_work = (1-(cost/sale))


    #Calculo del precio de venta y coste de los trabajos y su beneficio real
    @api.depends('cost_price_real_work_hour','total_real_hours', 'total_sp_real_work')
    def _compute_price_work_real(self):
        for record in self:
            record.total_cp_real_work = 0.0
            record.benefit_real_work = 0.0
            record.total_cp_real_work = record.total_real_hours * record.cost_price_real_work_hour
            if (record.total_cp_real_work != 0) and (record.total_sp_real_work != 0):
                record.benefit_real_work = (1-(record.total_cp_real_work/record.total_sp_real_work))

    #Calculo de los margenes segun ppto
    @api.depends('total_sp_work', 'total_sp_material', 'total_cp_work', 'total_cp_material')
    def _compute_sale_order(self):
        sale = 0.0
        cost = 0.0
        for record in self:
            record.margin_order_percent = 0.0
            sale = record.total_sp_work + record.total_sp_material
            cost = record.total_cp_work + record.total_cp_material
            record.margin_order_monetary = sale - cost
            if (cost != 0) and (sale != 0):
                record.margin_order_percent = (1-(cost/sale))

    #Calculo de los margenes reales    
    @api.depends('total_sp_real_work','total_sp_real_material','total_cp_real_material','total_real_hours','discount_real','cost_price_real_work_hour')
    def _compute_real(self):
        sale = 0.0
        cost = 0.0
        for record in self:
            record.margin_real_percent = 0.0
            sale = record.total_sp_real_work + record.total_sp_real_material
            cost = record.total_cp_real_material + (record.total_real_hours * record.cost_price_real_work_hour)                
            sale = sale - (sale * (record.discount_real / 100))
            record.margin_real_monetary = sale - cost
            if (cost != 0) and (sale != 0):
                record.margin_real_percent = (1-(cost/sale))

    #Calculo del precio de venta y coste total de los materiales y su beneficio según presupuesto    
    @api.depends('order_line', 'order_line.total_sp_material', 'order_line.total_cp_material', 'order_line.product_uom_qty', 'order_line.discount')
    def _compute_price_material(self):
        sale = 0.0
        cost = 0.0
        for order in self:
            order.benefit_material = 0.0
            for line in order.order_line:
                if line.product_id.type == 'service':
                    if line.auto_create_task:
                        if line.see_works_and_materials != 'only_works':
                            sale = sale + (line.total_sp_material * (line.product_uom_qty * (1 - (line.discount/100))))
                            cost = cost + (line.total_cp_material * line.product_uom_qty)
                else:
                    sale = sale + ((line.price_unit * line.product_uom_qty) * (1 - (line.discount/100)))
                    cost = cost + (line.purchase_price * line.product_uom_qty)
            order.total_sp_material = sale
            order.total_cp_material = cost
            if (cost != 0) and (sale != 0):
                order.benefit_material = (1-(cost/sale))

    #Calculo del beneficio real de materiales
    @api.depends('total_sp_real_material', 'total_cp_real_material')
    def _compute_price_material_real(self):
        for record in self:
            record.benefit_real_material = 0.0
            if (record.total_cp_real_material != 0) and (record.total_sp_real_material != 0):
                record.benefit_real_material = (1-(record.total_cp_real_material/record.total_sp_real_material))



        
