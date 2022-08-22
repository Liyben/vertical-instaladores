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