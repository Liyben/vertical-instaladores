# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.tools import float_is_zero, float_compare

import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):

    _inherit='sale.order.line'

    #Campos relacionales para trabajos y materiales
    task_works_ids = fields.One2many(
        comodel_name='sale.order.line.task.work', inverse_name='order_line_id', string='Trabajos', copy=True, 
        store=True, readonly=False, precompute=True, compute='_compute_materials_and_works')
    task_materials_ids = fields.One2many(
        comodel_name='sale.order.line.task.material', inverse_name='order_line_id', string='Materiales', copy=True, 
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
    detailed_time = fields.Boolean(string='Imp. trabajos')
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

    #Estado de la factura de una linea de pedido
    """ def _compute_invoice_status(self):
        super(SaleOrderLine, self)._compute_invoice_status()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if line.state not in ('sale', 'done'):
                line.invoice_status = 'no'
            elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                line.invoice_status = 'to invoice'
            elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
                line.invoice_status = 'invoiced'
            else:
                line.invoice_status = 'no' """

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
    @api.depends('task_works_ids', 'task_works_ids', 'task_works_ids.sale_price', 'task_materials_ids.sale_price', 'task_works_ids.hours', 'task_materials_ids.quantity')
    def _compute_price_unit(self):
        super()._compute_price_unit()
    
    #Computa el precio unitario de una linea de presupuesto teniendo en cuenta los materiales y mano de obra, si tuviera,
    #y los cambios que se hagan sobre ellos en la linea 
    #Overridden
    def _get_display_price(self):
        """Compute the displayed unit price for a given line.

        Overridden in custom flows:
        * where the price is not specified by the pricelist
        * where the discount is not specified by the pricelist

        Note: self.ensure_one()
        """
        self.ensure_one()
        
        #Producto Partida
        product_lst_price = 0.0
        product_standard_price = 0.0
        if self.auto_create_task and self.see_works_and_materials != False:
            #Guardamos los precios de la ficha de producto
            product_lst_price = self.product_id.list_price
            product_standard_price = self.product_id.standard_price

            #Actualizamos los precios de la ficha de producto con los precios de la linea de pedido
            self.product_id.write({
                'list_price' : (self.total_sp_material + self.total_sp_work),
                'standard_price' : (self.total_cp_material + self.total_cp_work),
                })
            
        pricelist_price = self._get_pricelist_price()

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return pricelist_price

        if not self.pricelist_item_id:
            # No pricelist rule found => no discount from pricelist
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()
        
        #Producto Partida
        if self.auto_create_task and self.see_works_and_materials != False:
            #Recuperamos los precios de la ficha producto previamente guardado
            self.product_id.write({
                'list_price' : product_lst_price,
                'standard_price' : product_standard_price,
                })

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)
    
    #Obtiene el precio del material o mano de obra segun tarifa	
    """ def _get_display_price_line(self, product, product_id, quantity):
        
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                    ptav.price_extra and
                    ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
            )


        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.order_id.pricelist_id.id).price

        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=product_id.uom_id.id)
        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product_id, quantity or 1.0, self.order_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, quantity, product_id.uom_id, self.order_id.pricelist_id.id)

        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())

        return max(base_price, final_price) """

    #Calculo del descuento según la tarifa	
    """ def _get_discount_line(self, product_id, quantity):
        if not (product_id and product_id.uom_id and 
                self.order_id.partner_id and 
                self.order_id.pricelist_id and 
                self.order_id.pricelist_id.discount_policy == 'without_discount' and 
                self.env.user.has_group('product.group_discount_per_so_line')):
            return

        product = product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=quantity,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=product_id.uom_id.id,
            fiscal_position=self.env.context.get('fiscal_position'))

        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=product_id.uom_id.id)

        price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product_id, quantity or 1.0, self.order_id.partner_id)
        new_list_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, quantity, product_id.uom_id, self.order_id.pricelist_id.id)

        if new_list_price != 0:
            if self.order_id.pricelist_id.currency_id != currency:
                #necesitamos que new_list_price este en la misma moneda que price, 
                #la cual esta en la moneda de la tarida del presupuesto
                new_list_price = currency._convert(
                    new_list_price, self.order_id.pricelist_id.currency_id,
                    self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
            
            discount = (new_list_price - price) / new_list_price * 100
            if (discount > 0):
                return discount """

    """ #Carga de los datos del producto en la linea de pedido al seleccionar dicho producto	
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        product = self.product_id
        if product:
            self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_in_project')
            if product.type == 'service':
                self.see_works_and_materials = product.see_works_and_materials
            else:
                self.see_works_and_materials = False

        if self.auto_create_task and self.see_works_and_materials != False:
            self.update({'task_works_ids' : False,
                    'task_materials_ids' : False,})

            work_list = []
            if self.see_works_and_materials != 'only_materials':
                for work in product.task_works_ids:
                    workforce = work.work_id.with_context(
                        lang=self.order_id.partner_id.lang,
                        partner=self.order_id.partner_id.id,
                        quantity=work.hours,
                        date=self.order_id.date_order,
                        pricelist=self.order_id.pricelist_id.id,
                        uom=work.work_id.uom_id.id)

                    work_list.append((0,0, {
                        'name' : work.name,
                        'work_id': work.work_id.id,
                        'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(workforce, work.work_id, work.hours), workforce.taxes_id, self.tax_id, self.company_id),
                        'cost_price_unit' : work.cost_price_unit,
                        'hours' : work.hours,
                        'discount' : self._get_discount_line(work.work_id, work.hours) or 0.0
                        }))

            material_list = []
            if self.see_works_and_materials != 'only_works':
                for material in product.task_materials_ids:
                    mat = material.material_id.with_context(
                            lang=self.order_id.partner_id.lang,
                            partner=self.order_id.partner_id.id,
                            quantity=material.quantity,
                            date=self.order_id.date_order,
                            pricelist=self.order_id.pricelist_id.id,
                            uom=material.material_id.uom_id.id)

                    material_list.append((0,0, {
                        'material_id' : material.material_id.id,
                        'name' : material.name,
                        'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(mat, material.material_id, material.quantity), mat.taxes_id, self.tax_id, self.company_id),
                        'cost_price_unit' : material.cost_price_unit,
                        'quantity' : material.quantity,
                        'discount' : self._get_discount_line(material.material_id, material.quantity) or 0.0
                        }))

            self.update({'task_works_ids' : work_list,
                    'task_materials_ids' : material_list,
                    'auto_create_task' : True,})

            #for line in self:
            #	line.price_unit = (line.total_sp_material + line.total_sp_work)

        else:
            self.update({'task_works_ids' : False,
                    'task_materials_ids' : False,
                    'auto_create_task' : False,})

        return result """

    #Calculo del precio de venta y coste del prodcuto tipo partida en la linea de pedido
    #al producirse algun cambio en los materiales, trabajos o mano de obra
    """ @api.onchange('task_materials_ids', 'task_works_ids')
    def _onchange_task_materials_works_workforce(self):
        product = self.product_id
        if product:
            self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_in_project')
        else:
            self.price_unit = 0.0
            return
            
        if self.auto_create_task and self.order_id.pricelist_id and self.order_id.partner_id:
            for line in self:
                #Guardamos los precios de la ficha de producto
                product_lst_price = line.product_id.lst_price
                product_standard_price = line.product_id.standard_price

                #Actualizamos los precios de la ficha de producto con los precios de la linea de pedido
                line.product_id.write({
                    'lst_price' : (line.total_sp_material + line.total_sp_work),
                    'standard_price' : (line.total_cp_material + line.total_cp_work),
                })

                #Aplicamos la tarifa
                product = line.product_id.with_context(
                    lang=line.order_id.partner_id.lang,
                    partner=line.order_id.partner_id.id,
                    quantity=line.product_uom_qty,
                    date=line.order_id.date_order,
                    pricelist=line.order_id.pricelist_id.id,
                    uom=line.product_uom.id,
                    fiscal_position=self.env.context.get('fiscal_position')
                )

                if line.product_id.apply_pricelist:
                    line.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
                else:
                    line.price_unit = line.total_sp_material + line.total_sp_work

                line.purchase_price = (line.total_cp_material + line.total_cp_work)

                #Recuperamos los precios de la ficha producto previamente guardado
                line.product_id.write({
                    'lst_price' : product_lst_price,
                    'standard_price' : product_standard_price,
                }) """

                
    #Cuando se cambie la cantida o las unidades del producto aplique la tarifa a los trabajos y
    #materiales si es de tipo partida el producto
    """ @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        result = super(SaleOrderLine, self).product_uom_change()
        product = self.product_id
        if product:
            self.auto_create_task = (product.service_tracking == 'task_global_project') or (product.service_tracking == 'task_in_project')

        if self.auto_create_task and self.order_id.pricelist_id and self.order_id.partner_id:
            for line in self:
                #Guardamos los precios de la ficha de producto
                product_lst_price = line.product_id.lst_price
                product_standard_price = line.product_id.standard_price

                #Actualizamos los precios de la ficha de producto con los precios de la linea de pedido
                line.product_id.write({
                    'lst_price' : (line.total_sp_material + line.total_sp_work),
                    'standard_price' : (line.total_cp_material + line.total_cp_work),
                })

                #Aplicamos la tarifa
                product = line.product_id.with_context(
                    lang=line.order_id.partner_id.lang,
                    partner=line.order_id.partner_id.id,
                    quantity=line.product_uom_qty,
                    date=line.order_id.date_order,
                    pricelist=line.order_id.pricelist_id.id,
                    uom=line.product_uom.id,
                    fiscal_position=self.env.context.get('fiscal_position')
                )
                if line.product_id.apply_pricelist:
                    line.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
                else:
                    line.price_unit = line.total_sp_material + line.total_sp_work
                
                line.purchase_price = (line.total_cp_material + line.total_cp_work)

                #Recuperamos los precios de la ficha producto previamente guardado
                line.product_id.write({
                    'lst_price' : product_lst_price,
                    'standard_price' : product_standard_price,
                })

        return result """

    """ def update_prices(self):
        self.ensure_one()
        for line in self._get_update_prices_lines():
            
            if line.auto_create_task:
                for works in line.task_works_ids:
                    works._onchange_hours()
                    works._onchange_discount()
                for materials in line.task_materials_ids:
                    materials._onchange_quantity()
                    materials._onchange_discount()

            line.product_uom_change()
            line.discount = 0  # Force 0 as discount for the cases when _onchange_discount directly returns
            line._onchange_discount()
        self.show_update_pricelist = False
        self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ", self.pricelist_id.display_name))

    #Función que recalcula el precio de venta y coste del compuesto
    def product_action_recalculate(self):
        if self.auto_create_task and self.order_id.pricelist_id and self.order_id.partner_id:
            for line in self:
                #Guardamos los precios de la ficha de producto
                product_lst_price = line.product_id.lst_price
                product_standard_price = line.product_id.standard_price

                #Actualizamos los precios de la ficha de producto con los precios de la linea de pedido
                line.product_id.write({
                    'lst_price' : (line.total_sp_material + line.total_sp_work),
                    'standard_price' : (line.total_cp_material + line.total_cp_work),
                })

                #Aplicamos la tarifa
                product = line.product_id.with_context(
                    lang=line.order_id.partner_id.lang,
                    partner=line.order_id.partner_id.id,
                    quantity=line.product_uom_qty,
                    date=line.order_id.date_order,
                    pricelist=line.order_id.pricelist_id.id,
                    uom=line.product_uom.id,
                    fiscal_position=self.env.context.get('fiscal_position')
                )

                if line.product_id.apply_pricelist:
                    line.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
                else:
                    line.price_unit = line.total_sp_material + line.total_sp_work

                line.purchase_price = (line.total_cp_material + line.total_cp_work)

                #Recuperamos los precios de la ficha producto previamente guardado
                line.product_id.write({
                    'lst_price' : product_lst_price,
                    'standard_price' : product_standard_price,
                }) """

    """ #Calculo de las horas estimadas al crear el parte de trabajo correspondiente a la linea de pedido
    def _convert_qty_company_hours(self,dest_company):
        company_time_uom_id = dest_company.project_time_mode_id
        if self.product_uom.id != company_time_uom_id.id and self.product_uom.category_id.id == company_time_uom_id.category_id.id:
            planned_hours = self.product_uom._compute_quantity(self.product_uom_qty, company_time_uom_id)
        else:
            planned_hours = sum(self.task_works_ids.mapped('hours')) * self.product_uom_qty
        return planned_hours
    """
    #Calculo de los valores necesarios para crear el proyecto correspondiente a la linea de pedido
    def _timesheet_create_project_prepare_values(self):
        """Generate project values"""
        values = super()._timesheet_create_project_prepare_values()
        values['picking_type_id'] = self.order_id.picking_type_id.id
        values['location_id'] = self.order_id.location_id.id
        values['location_dest_id'] = self.order_id.location_dest_id.id
        return values

    #Calculo de los valores necesarios para crear el parte de trabajo correspondiente a la linea de pedido
    def _timesheet_create_task_prepare_values(self, project):
        self.ensure_one()
        allocated_hours = 0.0
        if self.product_id.service_type not in ['milestones', 'manual']:
            allocated_hours = self._convert_qty_company_hours(self.company_id)
        sale_line_name_parts = self.name.split('\n')
        title = sale_line_name_parts[0] or self.product_id.name
        description = '<br/>'.join(sale_line_name_parts[1:])
        work_list = []
        for work in self.task_works_ids:
            work_list.append((0,0, {
                'work_id' : work.work_id.id,
                'name' : work.name,
                'hours' : work.hours * self.product_uom_qty,
                }))

        material_list = []

        for material in self.task_materials_ids:
            material_list.append((0,0, {
                'product_id' : material.material_id.id,
                'name' : material.name,
                'product_uom_qty' : material.quantity * self.product_uom_qty,
                'product_uom' : material.material_id.uom_id.id,
                'warehouse_id': self.order_id.location_id.warehouse_id.id,
                'picking_type_id' : self.order_id.picking_type_id.id,
                'location_id' : self.order_id.location_id.id,
                'location_dest_id' : self.order_id.location_dest_id.id,
                })) 

        return {
            'name': title if project.sale_line_id else '%s: %s' % (self.order_id.name or '', title),
            'analytic_account_id': project.analytic_account_id.id,
            'allocated_hours': allocated_hours,
            'partner_id': self.order_id.partner_id.id,
            'description': description,
            'work_to_do' : self.name + ' ' + str(self.product_uom_qty) + ' ' + self.product_uom.name + ' ' + '<br/>',
            'project_id': project.id,
            'sale_line_id': self.id,
            'sale_order_id': self.order_id.id,
            'company_id': project.company_id.id,
            'user_ids': False, 
            'move_ids': material_list,
            'task_works_ids': work_list,
            'oppor_id': self.order_id.opportunity_id.id or False, # Asocia con el aviso
            }

    #Calculo de los valores necesarios de la linea factura asociada a la linea de pedido, al crear la factura del pedido	
    """ def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)

        work_list = []
        material_list = []
        if res:
            if self.task_works_ids:
                for work in self.task_works_ids:
                    workforce = work.work_id.with_context(
                    lang=self.order_id.partner_id.lang,
                    partner=self.order_id.partner_id.id,
                    quantity=work.hours,
                    date=self.order_id.date_order,
                    pricelist=self.order_id.pricelist_id.id,
                    uom=work.work_id.uom_id.id)

                    work_list.append((0,0, {
                        'name' : work.name,
                        'work_id': work.work_id.id,
                        'sale_price_unit' : work.sale_price_unit,
                        #'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(workforce, work.work_id, work.hours), workforce.taxes_id, self.tax_id, self.company_id),
                        'cost_price_unit' : work.cost_price_unit,
                        'hours' : work.hours,
                        'discount' : self._get_discount_line(work.work_id, work.hours) or 0.0
                    }))
            else:
                work_list = False

            if self.task_materials_ids:
                for material in self.task_materials_ids:
                    mat = material.material_id.with_context(
                    lang=self.order_id.partner_id.lang,
                    partner=self.order_id.partner_id.id,
                    quantity=material.quantity,
                    date=self.order_id.date_order,
                    pricelist=self.order_id.pricelist_id.id,
                    uom=material.material_id.uom_id.id)

                    material_list.append((0,0, {
                        'material_id' : material.material_id.id,
                        'name' : material.name,
                        'sale_price_unit' : material.sale_price_unit,
                        #'sale_price_unit' : self.env['account.tax']._fix_tax_included_price_company(self._get_display_price_line(mat, material.material_id, material.quantity), mat.taxes_id, self.tax_id, self.company_id),
                        'cost_price_unit' : material.cost_price_unit,
                        'quantity' : material.quantity,
                        'discount' : self._get_discount_line(material.material_id, material.quantity) or 0.0
                    }))
            else:
                material_list = False

            res.update({'task_works_ids' : work_list,
                    'task_materials_ids' : material_list})

            res['auto_create_task'] = self.auto_create_task
            res['detailed_time'] = self.detailed_time
            res['detailed_price_time'] = self.detailed_price_time
            res['detailed_materials'] = self.detailed_materials
            res['detailed_price_materials'] = self.detailed_price_materials
            res['detailed_subtotal_price_time'] = self.detailed_subtotal_price_time
            res['detailed_subtotal_price_materials'] = self.detailed_subtotal_price_materials
            res['see_works_and_materials'] = self.see_works_and_materials

        return res
 """

