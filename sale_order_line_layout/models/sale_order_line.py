# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    layout_category_id = fields.Many2one('sale.order.line.layout', string='Seccion')

    @api.onchange('layout_category_id')
    def _onchange_layout_category_id(self):
        """
        Al cambiar la sección, copia su nombre a la descripción
        de la línea de pedido.
        """
        if self.layout_category_id:
            # Reemplazar completamente la descripción
            self.name = self.layout_category_id.name
            
            # (Alternativa): Agregar al texto existente
            # self.name = f"{self.layout_category_id.name} - {self.name or ''}"
