# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    
    _inherit='sale.order'

    #Lista de materialses usados en las partidas
    materials_ids = fields.One2many(
        comodel_name="sale.order.task.material",
        string="Materiales",
        inverse_name='order_id',
        check_company=True,
        compute='_compute_materials', 
        store=True,
    )
    #Lista de materialses usados en las partidas
    works_ids = fields.One2many(
        comodel_name="sale.order.task.work",
        string="Trabajos",
        inverse_name='order_id',
        check_company=True,
        compute='_compute_works', 
        store=True,
    )

    #Calculo del resumen de materiales
    @api.depends('order_line','order_line.task_materials_ids','order_line.task_materials_ids.material_id','order_line.task_materials_ids.sale_price_unit',
                 'order_line.task_materials_ids.cost_price_unit','order_line.task_materials_ids.discount','order_line.task_materials_ids.name',
                 'order_line.task_materials_ids.quantity')
    def _compute_materials(self):
        material_list = []
        for order in self:
            order.update({'materials_ids' : False})
            for line in order.order_line:
                if line.auto_create_task and line.see_works_and_materials != 'only_works':
                    for material in line.task_materials_ids:
                        if not material_list:
                            material_list.append((0,0, {
                                    #'order_id' : material.order_line_id.order_id.id,
                                    'material_id' : material.material_id.id,
                                    'name' : material.name,
                                    'sale_price_unit' : material.sale_price_unit,
                                    'cost_price_unit' : material.cost_price_unit,
                                    'quantity' : material.quantity * line.product_uom_qty,
                                    'discount' : material.discount,
                                }))
                        else:
                            encontrado = False
                            for item in material_list:
                                if encontrado:
                                    break

                                material_id = item[2]["material_id"]
                                sale_price = item[2]["sale_price_unit"]
                                cost_price = item[2]["cost_price_unit"]
                                discount = item[2]["discount"]
                                name = item[2]["name"]
                                if material_id == material.material_id.id and sale_price == material.sale_price_unit and cost_price == material.cost_price_unit and discount == material.discount and name.upper() == material.name.upper():
                                    item[2]["quantity"] = item[2]["quantity"] + (material.quantity * line.product_uom_qty)
                                    encontrado = True
                            if not encontrado:	
                                material_list.append((0,0, {
                                    #'order_id' : material.order_line_id.order_id.id,
                                    'material_id' : material.material_id.id,
                                    'name' : material.name,
                                    'sale_price_unit' : material.sale_price_unit,
                                    'cost_price_unit' : material.cost_price_unit,
                                    'quantity' : material.quantity * line.product_uom_qty,
                                    'discount' : material.discount,
                                }))

            order.update({'materials_ids' : material_list})

    #Calculo del resumen de trabajos
    @api.depends('order_line','order_line.task_works_ids','order_line.task_works_ids.material_id','order_line.task_works_ids.sale_price_unit',
                 'order_line.task_works_ids.cost_price_unit','order_line.task_works_ids.discount','order_line.task_works_ids.name',
                 'order_line.task_works_ids.quantity')
    def _compute_materials(self):
        work_list = []
        for order in self:
            order.update({'works_ids' : False})
            for line in order.order_line:
                if line.auto_create_task and line.see_works_and_materials != 'only_materials':
                    for work in line.task_works_ids:
                        if not work_list:
                            work_list.append((0,0, {
                                    #'order_id' : material.order_line_id.order_id.id,
                                    'work_id' : work.work_id.id,
                                    'name' : work.name,
                                    'sale_price_unit' : work.sale_price_unit,
                                    'cost_price_unit' : work.cost_price_unit,
                                    'hours' : work.hours * line.product_uom_qty,
                                    'discount' : work.discount,
                                }))
                        else:
                            encontrado = False
                            for item in work_list:
                                if encontrado:
                                    break

                                work_id = item[2]["work_id"]
                                sale_price = item[2]["sale_price_unit"]
                                cost_price = item[2]["cost_price_unit"]
                                discount = item[2]["discount"]
                                name = item[2]["name"]
                                if work_id == work.material_id.id and sale_price == work.sale_price_unit and cost_price == work.cost_price_unit and discount == work.discount and name.upper() == work.name.upper():
                                    item[2]["hours"] = item[2]["hours"] + (work.hours * line.product_uom_qty)
                                    encontrado = True
                            if not encontrado:	
                                work_list.append((0,0, {
                                    #'order_id' : material.order_line_id.order_id.id,
                                    'material_id' : work.material_id.id,
                                    'name' : work.name,
                                    'sale_price_unit' : work.sale_price_unit,
                                    'cost_price_unit' : work.cost_price_unit,
                                    'hours' : work.hours * line.product_uom_qty,
                                    'discount' : work.discount,
                                }))

            order.update({'works_ids' : work_list})
