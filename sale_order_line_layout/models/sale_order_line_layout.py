# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderLineLayout(models.Model):
    _name = 'sale.order.line.layout'
    _description = 'SaleOrderLineLayout'
    _order = 'sequence,id'

    name = fields.Char('Nombre', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Secuencia', required=True, default=10)
    pagebreak = fields.Boolean('Añadir salto de página')
