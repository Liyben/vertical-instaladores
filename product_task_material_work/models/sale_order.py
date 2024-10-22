# © 2024 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    
    _inherit='sale.order'

    #Numero de cliente
    ref = fields.Char(related='partner_id.ref', store=True, string='Nº. Cliente', precompute=True)

    #Campos para el stock desde la tarea
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Tipo de operación",
        readonly=False,
        domain="[('company_id', '=', company_id)]",
        index=True,
        check_company=True,
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Ubicación de origen",
        readonly=False,
        check_company=True,
        index=True,
    )
    location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Ubicación destino",
        readonly=False,
        index=True,
        check_company=True,
    )

    #Grupo cuenta analitica
    #account_analytic_group_id = fields.Many2one('account.analytic.group', string='Grupo', check_company=True) 

    #Método para los datos de la cuenta analitica
    """ def _prepare_analytic_account_data(self, prefix=None):
        analytic_account_vals = super(SaleOrder, self)._prepare_analytic_account_data(prefix)

        for order in self: 
            if order.account_analytic_group_id:
                analytic_account_vals.update({'group_id': order.account_analytic_group_id.id})

        return analytic_account_vals """

        
