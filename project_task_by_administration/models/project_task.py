# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import html2text

class ProjectTask(models.Model):
    _inherit = 'project.task'

    #Indica si un PT es facturable por administracion o no
    by_administration = fields.Boolean(string='Por Administración', default=False)

    #Al pasar un PT a por administracion recalculamos su linea de pedido asociada
    #con los cambios introducidos en el PT
    
    def sale_order_action_recalculate(self):
        self._check_sale_line_exist() #Comprobamos si existe linea de pedido asociada
        self._check_sale_line_state() #Comprobamos en que estado se encuentra
        if self.task_to_invoice:
            #Calculamos la nueva lista de materiales que le pasaremos a la linea de pedido asociada
            material_list = []
            if self.move_ids:
                for move in self.move_ids:
                    material_list.append((0,0, {
                        'material_id' : move.product_id.id,
                        'name' : move.name,
                        'quantity' : move.product_uom_qty,
                        'sale_price_unit' : move.product_id.lst_price,
                        'cost_price_unit' : move.product_id.standard_price,
                        'discount' : 0.0
                        }))
            else:
                material_list = False

            #Calculamos la nueva lista de trabajos que le pasaremos a la linea de pedido asociada
            work_list = []
            if self.timesheet_ids:
                for work in self.timesheet_ids:
                    work_list.append((0,0, {
                            'name' : work.name,
                            'work_id': work.employee_id.work_id.id,
                            'hours' : work.unit_amount,
                            'sale_price_unit' : work.employee_id.work_id.lst_price if work.employee_id.work_id else 0.0,
                            'cost_price_unit' : work.employee_id.work_id.standard_price if work.employee_id.work_id else 0.0,
                            'discount' : 0.0
                        }))
            else:
                work_list = False

            # Verificamos si el campo 'code' existe y tiene contenido
            task_reference = f"{self.code} - " if hasattr(self, 'code') and self.code else ""
            nameToText = f"Parte de Trabajo: {task_reference}{self.name or ''}"

            # Concatenación de trabajos a realizar (evitando que se pegue al nombre)
            if self.work_to_do:
                # Añadimos un salto de línea antes del texto adicional para mayor claridad
                nameToText += f"\n\n{self.work_to_do}"

            #Limpiamos la lista de trabajos y materiales de la linea de pedido asociada
            self.sale_line_id.write({'task_works_ids' : [(5, 0, 0)],
                                'task_materials_ids' : [(5, 0, 0)]
                                })

            #Actualizamos con las nuevas listas de trabajos y materiales de la linea de pedido asociada
            self.sale_line_id.write({'task_works_ids' : work_list,
                                'task_materials_ids' : material_list,
                                'name' : html2text.html2text(nameToText)
                                })
            self.sale_line_id._compute_price_unit()

            #Cambiamos el valor del campo Por Administracio del PT
            if not self.by_administration:
                self.by_administration = not self.by_administration

    #Funcion que comprueba si el PT tiene linea de pedido
    def _check_sale_line_exist(self):
        if not self.sale_line_id:
            raise ValidationError(_('No existe ninguna linea de pedido asociada al PT.'))

    #Comprobamos el estado de la linea de pedido, en el caso que no cumpla los requisitos necesarios
    #para ser facturada, se lanza una excepcion que avisa al usuario con un mensaje
    def _check_sale_line_state(self, sale_line_id=False):
        sale_lines = self.mapped('sale_line_id')
        if sale_line_id:
            sale_lines |= self.env['sale.order.line'].browse(sale_line_id)
        for sale_line in sale_lines:
            #Comprobamos la cantidad de la linea de pedido
            if sale_line.product_uom_qty == 0:
                raise ValidationError(_('No puede crear/modificar un PT relacionado con '
                    'una cantidad en la linea de pedido igual a 0. Compruebe las lineas de pedido.'))
            #Comprobamos el estado de la linea de pedido
            if (sale_line.state in ('done', 'cancel') or 
                sale_line.invoice_status == 'invoiced'): 
                raise ValidationError(_('No puede crear/modificar un PT relacionado con '
                    'una linea de pedido facturada, realizada o cancelada'))