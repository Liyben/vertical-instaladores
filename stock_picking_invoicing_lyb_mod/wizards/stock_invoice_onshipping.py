# © 2022 Liyben
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockInvoiceOnshipping(models.TransientModel):
	_inherit = "stock.invoice.onshipping"

	
	def _load_pickings(self):
		pickings = super()._load_pickings()
		if 'assigned' in pickings.mapped("state") or 'cancel' in pickings.mapped("state") or 'draft' in pickings.mapped("state") or 'waiting' in pickings.mapped("state") or 'confirmed' in pickings.mapped("state"):
			raise UserError(_("¡Todos los albaranes deben estar en estado Hecho!"))
		pickings.set_sale_to_invoiced()
		pickings.set_purchase_to_invoiced()
		return pickings

	def _get_invoice_line_values(self, moves, invoice_values, invoice):
		"""
		Create invoice line values from given moves
		:param moves: stock.move
		:param invoice: account.move
		:return: dict
		"""
		name = ", ".join(moves.mapped("name"))
		move = fields.first(moves)
		product = move.product_id
		fiscal_position = self.env["account.fiscal.position"].browse(
			invoice_values["fiscal_position_id"]
		)
		partner_id = self.env["res.partner"].browse(invoice_values["partner_id"])
		categ = product.categ_id
		inv_type = invoice_values["move_type"]
		if inv_type in ("out_invoice", "out_refund"):
			account = product.property_account_income_id
			if not account:
				account = categ.property_account_income_categ_id
		else:
			account = product.property_account_expense_id
			if not account:
				account = categ.property_account_expense_categ_id
		account = move._get_account(fiscal_position, account)
		quantity = 0
		move_line_ids = []
		sale_line_ids = []
		purchase_line_id = False
		for move in moves:
			qty = move.product_uom_qty
			loc = move.location_id
			loc_dst = move.location_dest_id
			# Better to understand with IF/ELIF than many OR
			if inv_type == "out_invoice" and loc.usage == "customer":
				qty *= -1
			elif inv_type == "out_refund" and loc_dst.usage == "customer":
				qty *= -1
			elif inv_type == "in_invoice" and loc_dst.usage == "supplier":
				qty *= -1
			elif inv_type == "in_refund" and loc.usage == "supplier":
				qty *= -1
			quantity += qty
			# Ponemos las lineas de pedido de venta/compra como facturada
			if move.sale_line_id:
				sale_line = move.sale_line_id
				sale_line.update({'invoice_status': 'invoiced'})
				#Añadimos la linea de pedido de venta para la factura
				sale_line_ids.append((4, sale_line.id, False))
			if move.purchase_line_id:
				purchase = move.purchase_line_id.order_id
				purchase.update({'invoice_status': 'invoiced'})
				#Añadimos la linea de pedido de compra para la factura
				purchase_line_id = move.purchase_line_id.id
			move_line_ids.append((4, move.id, False))

		taxes = moves._get_taxes(fiscal_position, inv_type)
		price = moves._get_price_unit_invoice(inv_type, partner_id, quantity)
		#discount = moves._get_discount(inv_type)
		line_obj = self.env["account.move.line"]
		values = line_obj.default_get(line_obj.fields_get().keys())
		values.update(
			{
				"name": name,
				"account_id": account.id,
				"product_id": product.id,
				"product_uom_id": product.uom_id.id,
				"quantity": quantity,
				"price_unit": price,
				"tax_ids": [(6, 0, taxes.ids)],
				"move_line_ids": move_line_ids,
				"move_id": invoice.id,
				#'discount': discount,
				'sale_line_ids' : sale_line_ids,
				'purchase_line_id' : purchase_line_id,
			}
		)
		values = self._simulate_invoice_line_onchange(values, price_unit=price)
		values.update({"name": name})
		return values

	def _action_generate_invoices(self):
		"""
		Action to generate invoices based on pickings
		:return: account.move recordset
		"""
		pickings = self._load_pickings()
		company = pickings.mapped("company_id")
		if company and company != self.env.company:
			raise UserError(_("All pickings are not related to your company!"))
		pick_list = self._group_pickings(pickings)
		invoices = self.env["account.move"].browse()
		for pickings in pick_list:
			moves = pickings.mapped("move_lines")
			grouped_moves_list = self._group_moves(moves)
			parts = self.ungroup_moves(grouped_moves_list)
			for moves_list in parts:
				#_logger.debug('Parts: %s',moves_list)
				invoice, invoice_values = self._build_invoice_values_from_pickings(
					pickings
				)
				lines = [(5, 0, {})]
				line_values = False
				for moves in moves_list:
					#_logger.debug('Mvees: %s',moves)
					line_values = self._get_invoice_line_values(
						moves, invoice_values, invoice
					)
					if line_values:
						if moves.picking_id.picking_type_code == 'incoming' and moves.picking_id.supplier_pick_number:
							lines.append((0,0,
								{
									"name": "Nº. albarán proveedor: " + moves.picking_id.supplier_pick_number,
									"display_type": "line_section",
									"account_id": False,
									"currency_id": invoice.currency_id.id,
								}))
						lines.append((0, 0, line_values))
				if line_values:  # Only create the invoice if it has lines
					invoice_values["invoice_line_ids"] = lines
					invoice_values["invoice_date"] = self.invoice_date
					# this is needed otherwise invoice_line_ids are removed
					# in _move_autocomplete_invoice_lines_create
					# and no invoice line is created
					invoice_values.pop("line_ids")
					invoice = self._create_invoice(invoice_values)
					invoice._onchange_invoice_line_ids()
					invoice._compute_amount()
					invoices |= invoice
		return invoices