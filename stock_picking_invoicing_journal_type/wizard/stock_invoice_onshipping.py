# © 2020 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockInvoiceOnshipping(models.TransientModel):
	_inherit = 'stock.invoice.onshipping'
	
	
	@api.model
	def _default_default_debit_account_id(self):
		
		default_debit_account = False
		#Obtenemos el albaran actual
		active_ids = self.env.context.get('active_ids', [])
		if active_ids:
			active_ids = active_ids[0]
		pick_obj = self.env['stock.picking']
		picking = pick_obj.browse(active_ids)

		#Obtenemos el id de la cuenta deudora por defecto del Pedido de venta
		if (self._get_journal_type() == 'sale') and picking and picking.sale_id.type_id.default_debit_account_id:
			default_debit_account = picking.sale_id.type_id.default_debit_account_id.id

		return default_debit_account

	@api.model
	def _default_account_id(self): 
		
		default_account = False
		#Obtenemos el albaran actual
		active_ids = self.env.context.get('active_ids', [])
		if active_ids:
			active_ids = active_ids[0]
		pick_obj = self.env['stock.picking']
		picking = pick_obj.browse(active_ids)

		#Obtenemos el id de la cuenta a cobrar por defecto del Pedido de venta
		if (self._get_journal_type() == 'sale') and picking and picking.sale_id.type_id.account_id:
			default_account = picking.sale_id.type_id.account_id.id

		return default_account
	
	@api.model
	def _default_tax_id(self): 
		
		default_tax = False
		#Obtenemos el albaran actual
		active_ids = self.env.context.get('active_ids', [])
		if active_ids:
			active_ids = active_ids[0]
		pick_obj = self.env['stock.picking']
		picking = pick_obj.browse(active_ids)

		#Obtenemos los ids de los impuestos del Pedido de venta
		if (self._get_journal_type() == 'sale') and picking and picking.sale_id.type_id.tax_id:
			company_id = self.env.context.get('force_company', self.env.user.company_id.id)
			default_tax = picking.sale_id.type_id.tax_id.filtered(lambda r: r.company_id.id == company_id)

		return default_tax

	@api.model
	def _default_order_type(self): 
		
		default_type = False
		#Obtenemos el albaran actual
		active_ids = self.env.context.get('active_ids', [])
		if active_ids:
			active_ids = active_ids[0]
		pick_obj = self.env['stock.picking']
		picking = pick_obj.browse(active_ids)

		#Obtenemos el id de la cuenta a cobrar por defecto del Pedido de venta
		if (self._get_journal_type() == 'sale') and picking and picking.sale_id.type_id:
			default_type = picking.sale_id.type_id.id

		return default_type

	default_debit_account_id = fields.Many2one('account.account', string='Cuenta deudora por defecto', domain=[('deprecated', '=', False)], 
		help="Actúa como una cuenta por defecto para importes en el debe", default=_default_default_debit_account_id)

	account_id = fields.Many2one('account.account', string='Cuenta a cobrar por defecto',
		domain=[('deprecated', '=', False)], help="La cuenta que será usada para la factura",
		default=_default_account_id)
	
	tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)],
		default=_default_tax_id)
	
	type_id = fields.Many2one('sale.order.type', string='Sale Type', default=_default_order_type)

	@api.model
	def _default_journal(self, journal_type):
		"""
		Get the default journal based on the given type
		:param journal_type: str
		:return: account.journal recordset
		"""
		default_journal = super()._default_journal(journal_type)

		#Obtenemos el albaran actual
		active_ids = self.env.context.get('active_ids', [])
		if active_ids:
			active_ids = active_ids[0]
		pick_obj = self.env['stock.picking']
		picking = pick_obj.browse(active_ids)

		#Obtenemos el id del diario del Pedido de venta
		if journal_type == 'sale' and picking and picking.sale_id and picking.sale_id.type_id and picking.sale_id.type_id.journal_id:
			default_journal = picking.sale_id.type_id.journal_id.id

		return default_journal

	@api.multi
	def _get_invoice_line_values(self, moves, invoice_values, invoice):

		values = super()._get_invoice_line_values(moves, invoice_values, invoice)

		if self.default_debit_account_id:
			values.update({
				'account_id': self.default_debit_account_id.id,
				})
		
		if self.tax_id:
			values.update({
				'invoice_line_tax_ids': [(6, 0, self.tax_id.ids)],
			})
		
		return values

	@api.multi
	def _build_invoice_values_from_pickings(self, pickings):
		
		invoice, values = super()._build_invoice_values_from_pickings(pickings)

		if self.account_id:
			values.update({
				'account_id': self.account_id.id,
				})
			invoice.update({
				'account_id': self.account_id.id,
				})

		if self.type_id:
			values.update({
				'sale_type_id': self.type_id.id,
				})
			invoice.update({
				'sale_type_id': self.type_id.id,
				})

		
		return invoice, values

	@api.constrains('sale_journal')
	def check_sale_journal(self):
		#Obtenemos el albaran actual
		active_ids = self.env.context.get('active_ids', [])
		if active_ids:
			active_ids = active_ids[0]
		pick_obj = self.env['stock.picking']
		picking = pick_obj.browse(active_ids)

		if picking and picking.sale_id and picking.sale_id.type_id and (picking.sale_id.type_id.journal_id != self.sale_journal):
			raise UserError(_('El diario seleccionado es distinto al configurado en su Pedido de Venta. Si desea crear la factura ambos diarios deben '
							'coincidir.'))
