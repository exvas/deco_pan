# Copyright (c) 2024, sammish and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe import _, msgprint, throw
from frappe.model.document import Document
from erpnext.controllers.selling_controller import SellingController
from erpnext.controllers.accounts_controller import validate_account_head
from erpnext.accounts.party import get_due_date, get_party_account, get_party_details
from erpnext.accounts.utils import cancel_exchange_gain_loss_journal, get_account_currency
from frappe.utils import add_days, cint, cstr, flt, formatdate, get_link_to_form, getdate, nowdate
from erpnext.accounts.utils import (
	create_gain_loss_journal,
	get_currency_precision,
	get_fiscal_years,
	validate_fiscal_year,
)
from datetime import datetime, date
import json
from erpnext.stock.doctype.bin.bin import update_qty as update_bin_qty, get_bin_details
from erpnext.stock.utils import (
	get_combine_datetime,
	get_incoming_outgoing_rate_for_cancel,
	get_incoming_rate,
	get_or_make_bin,
	get_serial_nos_data,
	get_stock_balance,
	get_valuation_method,
)
from frappe.query_builder.functions import Coalesce, CombineDatetime, Sum
from frappe.query_builder import Case, Order
from erpnext.accounts.general_ledger import (
	make_gl_entries,
	make_reverse_gl_entries,
	process_gl_map,
)
from erpnext.stock.get_item_details import get_bin_details, get_conversion_factor
from erpnext.stock.stock_ledger import make_sl_entries
class CashInvoice(Document):
	@frappe.whitelist()
	def get_stock_details(self, item_code=None, validate_stock=False):
		if item_code:
			bin_details = self.get_item_bin(item_code, self.warehouse)
			last_salling_rate = frappe.db.sql("""
				SELECT CII.rate
				FROM `tabCash Invoice Item` CII
				INNER JOIN `tabCash Invoice` CI
				ON CI.name = CII.parent
				WHERE 
					CI.customer = '{0}' and
					CII.docstatus = 1 and
					CII.item_code = '{1}'
				ORDER BY CI.creation ASC
				LIMIT 1
			""".format(self.customer, item_code))
			bin_details["last_selling_rate"] = last_salling_rate[0][0] if last_salling_rate else 0
			return bin_details
		else:
			for i in self.items:
				actual_qty = 0
				print(self.warehouse)
				print(i.item_code)
				bin_details = self.get_item_bin(i.item_code, self.warehouse)
				if bin_details.get("actual_qty"):
					if validate_stock:
						frappe.msgprint("{0} is not available in {1}".format(i.item_code, self.warehouse))
					elif not validate_stock:
						actual_qty = bin_details.get("actual_qty")
				i.available_qty = actual_qty

	def get_item_bin(self, item_code, warehouse):
		bin_name = frappe.db.exists("Bin", {"item_code": item_code, "warehouse": warehouse})
		if bin_name:
			return frappe.get_doc("Bin", bin_name).as_dict()
		else:
			return {}

	def validate(self):
		self.balance_amount = self.advance_paid_amount - self.paid_amount
		if self.advance_paid_amount < self.paid_amount:
			frappe.throw("Paid amount cannot be less than Invoice Amount")
		self.validate_debit_to_acc()
		self.validate_item_cost_centers()
		self.validate_income_account()

	def validate_debit_to_acc(self):
		if not self.debit_to:
			self.debit_to = get_party_account("Customer", self.customer, self.company)
			if not self.debit_to:
				self.raise_missing_debit_credit_account_error("Customer", self.customer)

		account = frappe.get_cached_value(
			"Account", self.debit_to, ["account_type", "report_type", "account_currency"], as_dict=True
		)

		if not account:
			frappe.throw(_("Debit To is required"), title=_("Account Missing"))

		if account.report_type != "Balance Sheet":
			msg = (
				_("Please ensure {} account is a Balance Sheet account.").format(frappe.bold("Debit To"))
				+ " "
			)
			msg += _(
				"You can change the parent account to a Balance Sheet account or select a different account."
			)
			frappe.throw(msg, title=_("Invalid Account"))

		if self.customer and account.account_type != "Receivable":
			msg = (
				_("Please ensure {} account {} is a Receivable account.").format(
					frappe.bold("Debit To"), frappe.bold(self.debit_to)
				)
				+ " "
			)
			msg += _("Change the account type to Receivable or select a different account.")
			frappe.throw(msg, title=_("Invalid Account"))

		self.party_account_currency = account.account_currency

	def validate_item_cost_centers(self):
		for item in self.items:
			cost_center_company = frappe.get_cached_value("Cost Center", item.cost_center, "company")
			if cost_center_company != self.company:
				frappe.throw(
					_("Row #{0}: Cost Center {1} does not belong to company {2}").format(
						frappe.bold(item.idx), frappe.bold(item.cost_center), frappe.bold(self.company)
					)
				)
		
	def validate_income_account(self):
		for item in self.get("items"):
			validate_account_head(item.idx, item.income_account, self.company, "Income")

	@frappe.whitelist()
	def set_missing_values(self, for_validate=False):
		pass

	def on_submit(self):
		company = frappe.get_doc("Company", self.company)
		tvr = self.calcluate_valuation_amount()

		# Update Stock
		self.create_stock_ledger_entry()

		# Cash Accounting GL Entries
		self.create_debit_gl_entry(company.default_currency)
		self.create_credit_gl_entry(company.default_currency)

		# Items Account GL Entries
		self.create_item_gl_entry(
			company.default_currency, 
			company.default_expense_account, 
			company.default_inventory_account ,
			tvr
		)

		self.status = "Paid"

	def create_stock_ledger_entry(self):
		for item in self.items:
			warehouse = item.warehouse or self.warehouse
			bin_name = get_or_make_bin(item.item_code, warehouse)

			if not frappe.db.exists("Bin", bin_name):
				frappe.throw("Could not find stock details of {0}".format(item.item_code))
			
			bin_doc = frappe.get_doc("Bin", bin_name)
			if bin_doc.actual_qty <= 0:
				frappe.throw("{0} is not available in {1}".format(item.item_code, warehouse))

			stock_dif = bin_doc.actual_qty - item.qty
			if stock_dif < 0:
				frappe.throw("{0} requires {1} more qty of {2}".format(warehouse, (stock_dif*-1)), item.item_code)
			stock_queue = []
			stock_queue.append([bin_doc.actual_qty - item.qty, bin_doc.valuation_rate])
			sle_doc = frappe.new_doc("Stock Ledger Entry")
			sle_doc.item_code = item.item_code
			sle_doc.voucher_type = "Cash Invoice"
			sle_doc.voucher_no = self.name
			sle_doc.voucher_detail_no = item.name
			sle_doc.warehouse = item.warehouse or self.warehouse
			sle_doc.posting_time = self.posting_time
			sle_doc.posting_date = datetime.today()
			sle_doc.actual_qty = -1 * item.qty
			sle_doc.qty_after_transaction = bin_doc.actual_qty - item.qty
			sle_doc.incoming_rate = item.rate
			sle_doc.valuation_rate = bin_doc.valuation_rate
			sle_doc.stock_uom = frappe.db.get_value("Item", item.item_code, "stock_uom")
			sle_doc.stock_value = bin_doc.valuation_rate * (bin_doc.actual_qty - item.qty)
			sle_doc.stock_value_difference = bin_doc.stock_value - (bin_doc.valuation_rate * (bin_doc.actual_qty - item.qty))
			sle_doc.stock_queue = json.dumps(stock_queue)
			sle_doc.fiscal_year = self.validate_fiscal_year()
			sle_doc.company = self.company
			sle_doc.save(ignore_permissions=True)
			sle_doc.submit()
			# Update Bin
			self.update_bin(bin_name, sle_doc.as_dict())

	def create_debit_gl_entry(self, currency):
		# Debit against Debit Account
		settings = frappe.get_doc("Deco Pan Settings")
		gl_doc = frappe.new_doc("GL Entry")
		gl_doc.posting_date = self.date
		gl_doc.transaction_date = date.today()
		gl_doc.account = self.debit_to
		gl_doc.cost_center = self.cost_center
		gl_doc.party_type = "Customer"
		gl_doc.party = self.customer
		gl_doc.debit = self.rounded_total or self.grand_total
		gl_doc.credit = 0
		gl_doc.account_currency = get_account_currency(self.debit_to)
		gl_doc.debit_in_account_currency = self.rounded_total or self.grand_total
		gl_doc.credit_in_account_currency = 0
		gl_doc.against = settings.default_income_account
		gl_doc.against_voucher_type = "Cash Invoice"
		gl_doc.against_voucher = self.name
		gl_doc.voucher_type = "Cash Invoice"
		gl_doc.voucher_subtype = "Debit Note"
		gl_doc.voucher_no = self.name
		gl_doc.remarks = self.remarks
		gl_doc.is_advance = "No"
		gl_doc.fiscal_year = self.validate_fiscal_year()
		gl_doc.company = self.company
		gl_doc.due_date = self.date
		gl_doc.transaction_currency = currency
		gl_doc.debit_in_transaction_currency = self.rounded_total or self.grand_total
		gl_doc.credit_in_transaction_currency = 0
		gl_doc.transaction_exchange_rate = 1
		gl_doc.save(ignore_permissions=True)
		gl_doc.submit()

		# Debit Againt Payment Mode
		gl_doc = frappe.new_doc("GL Entry")
		gl_doc.posting_date = self.date
		gl_doc.transaction_date = date.today()
		gl_doc.account = self.payment_mode
		gl_doc.cost_center = self.cost_center
		gl_doc.party_type = "Customer"
		gl_doc.party = self.customer
		gl_doc.debit = self.rounded_total or self.grand_total
		gl_doc.credit = 0
		gl_doc.account_currency = get_account_currency(self.payment_mode)
		gl_doc.debit_in_account_currency = self.rounded_total or self.grand_total
		gl_doc.credit_in_account_currency = 0
		gl_doc.against = self.customer
		gl_doc.against_voucher_type = "Cash Invoice"
		gl_doc.against_voucher = self.name
		gl_doc.voucher_type = "Cash Invoice"
		gl_doc.voucher_subtype = "Debit Note"
		gl_doc.voucher_no = self.name
		gl_doc.remarks = self.remarks
		gl_doc.is_advance = "No"
		gl_doc.fiscal_year = self.validate_fiscal_year()
		gl_doc.company = self.company
		gl_doc.due_date = self.date
		gl_doc.transaction_currency = currency
		gl_doc.debit_in_transaction_currency = self.rounded_total or self.grand_total
		gl_doc.credit_in_transaction_currency = 0
		gl_doc.transaction_exchange_rate = 1
		gl_doc.save(ignore_permissions=True)
		gl_doc.submit()

	def create_credit_gl_entry(self, currency):
		# Credit Against Debit account
		settings = frappe.get_doc("Deco Pan Settings")
		gl_doc = frappe.new_doc("GL Entry")
		gl_doc.posting_date = self.date
		gl_doc.transaction_date = date.today()
		gl_doc.account = self.debit_to
		gl_doc.cost_center = self.cost_center
		gl_doc.party_type = "Customer"
		gl_doc.party = self.customer
		gl_doc.debit = 0
		gl_doc.credit = self.rounded_total or self.grand_total
		gl_doc.account_currency = get_account_currency(self.debit_to)
		gl_doc.debit_in_account_currency = 0
		gl_doc.credit_in_account_currency = self.rounded_total or self.grand_total
		gl_doc.against = settings.payment_mode
		gl_doc.against_voucher_type = "Cash Invoice"
		gl_doc.against_voucher = self.name
		gl_doc.voucher_type = "Cash Invoice"
		gl_doc.voucher_subtype = "Debit Note"
		gl_doc.voucher_no = self.name
		gl_doc.remarks = self.remarks
		gl_doc.is_advance = "No"
		gl_doc.fiscal_year = self.validate_fiscal_year()
		gl_doc.company = self.company
		gl_doc.due_date = self.date
		gl_doc.transaction_currency = currency
		gl_doc.debit_in_transaction_currency = 0
		gl_doc.credit_in_transaction_currency = self.rounded_total or self.grand_total
		gl_doc.transaction_exchange_rate = 1
		gl_doc.save(ignore_permissions=True)
		gl_doc.submit()


		# Credit Against Income Account
		gl_doc = frappe.new_doc("GL Entry")
		gl_doc.posting_date = self.date
		gl_doc.transaction_date = date.today()
		gl_doc.account = settings.default_income_account
		gl_doc.cost_center = self.cost_center
		gl_doc.party_type = "Customer"
		gl_doc.party = self.customer
		gl_doc.debit = 0
		gl_doc.credit = self.rounded_total or self.grand_total
		gl_doc.account_currency = get_account_currency(settings.default_income_account)
		gl_doc.debit_in_account_currency = 0
		gl_doc.credit_in_account_currency = self.rounded_total or self.grand_total
		gl_doc.against = self.customer
		gl_doc.against_voucher_type = "Cash Invoice"
		gl_doc.against_voucher = self.name
		gl_doc.voucher_type = "Cash Invoice"
		gl_doc.voucher_subtype = "Debit Note"
		gl_doc.voucher_no = self.name
		gl_doc.remarks = self.remarks
		gl_doc.is_advance = "No"
		gl_doc.fiscal_year = self.validate_fiscal_year()
		gl_doc.company = self.company
		gl_doc.due_date = self.date
		gl_doc.transaction_currency = currency
		gl_doc.debit_in_transaction_currency = 0
		gl_doc.credit_in_transaction_currency = self.rounded_total or self.grand_total
		gl_doc.transaction_exchange_rate = 1
		gl_doc.save(ignore_permissions=True)
		gl_doc.submit()

	def create_item_gl_entry(self, currency, expense_account, invetory_account, tvr):
		# Debit Againt Default Expense Account
		gl_doc = frappe.new_doc("GL Entry")
		gl_doc.posting_date = self.date
		gl_doc.transaction_date = date.today()
		gl_doc.account = expense_account
		gl_doc.cost_center = self.cost_center
		gl_doc.party_type = "Customer"
		gl_doc.party = self.customer
		gl_doc.debit = tvr
		gl_doc.credit = 0
		gl_doc.account_currency = get_account_currency(expense_account)
		gl_doc.debit_in_account_currency = tvr
		gl_doc.credit_in_account_currency = 0
		gl_doc.against = self.customer
		gl_doc.against_voucher_type = "Cash Invoice"
		gl_doc.against_voucher = self.name
		gl_doc.voucher_type = "Cash Invoice"
		gl_doc.voucher_subtype = "Debit Note"
		gl_doc.voucher_no = self.name
		gl_doc.remarks = self.remarks
		gl_doc.is_advance = "No"
		gl_doc.fiscal_year = self.validate_fiscal_year()
		gl_doc.company = self.company
		gl_doc.due_date = self.date
		gl_doc.transaction_currency = currency
		gl_doc.debit_in_transaction_currency = tvr
		gl_doc.credit_in_transaction_currency = 0
		gl_doc.transaction_exchange_rate = 1
		gl_doc.save(ignore_permissions=True)
		gl_doc.submit()

		# Credit Againt Default Inventory Account
		gl_doc = frappe.new_doc("GL Entry")
		gl_doc.posting_date = self.date
		gl_doc.transaction_date = date.today()
		gl_doc.account = invetory_account
		gl_doc.cost_center = self.cost_center
		gl_doc.party_type = "Customer"
		gl_doc.party = self.customer
		gl_doc.debit = 0
		gl_doc.credit = tvr
		gl_doc.account_currency = get_account_currency(invetory_account)
		gl_doc.debit_in_account_currency = 0
		gl_doc.credit_in_account_currency = tvr
		gl_doc.against = self.customer
		gl_doc.against_voucher_type = "Cash Invoice"
		gl_doc.against_voucher = self.name
		gl_doc.voucher_type = "Cash Invoice"
		gl_doc.voucher_subtype = "Debit Note"
		gl_doc.voucher_no = self.name
		gl_doc.remarks = self.remarks
		gl_doc.is_advance = "No"
		gl_doc.fiscal_year = self.validate_fiscal_year()
		gl_doc.company = self.company
		gl_doc.due_date = self.date
		gl_doc.transaction_currency = currency
		gl_doc.debit_in_transaction_currency = 0
		gl_doc.credit_in_transaction_currency = tvr
		gl_doc.transaction_exchange_rate = 1
		gl_doc.save(ignore_permissions=True)
		gl_doc.submit()

	def calcluate_valuation_amount(self):
		total_valuation_rate = 0
		for item in self.items:
			if not frappe.db.exists("Bin", {"item_code": item.item_code, "warehouse": self.warehouse}):
				frappe.throw("Item {1} not found in {0}".format(self.warehouse, item.item_code))
			bin_doc = frappe.get_last_doc("Bin", {"item_code": item.item_code, "warehouse": self.warehouse})
			total_valuation_rate += item.qty * bin_doc.valuation_rate

		return total_valuation_rate
	
	def validate_fiscal_year(self):
		fiscal_year = None
		fiscal_years = get_fiscal_years(self.date, company=self.company)
		if len(fiscal_years) > 1:
			frappe.throw(
				_("Multiple fiscal years exist for the date {0}. Please set company in Fiscal Year").format(
					formatdate(self.date)
				)
			)
		else:
			fiscal_year = fiscal_years[0][0]
		if not fiscal_year:
			frappe.throw(
				_("Ffiscal year not exist for the date {0}. Please set company in Fiscal Year").format(
					formatdate(self.date)
				)
			)
		return fiscal_year

	def update_bin(self, bin_name, args):
		bin_details = get_bin_details(bin_name, self.warehouse)
		# actual qty is already updated by processing current voucher
		actual_qty = bin_details.actual_qty or 0.0
		sle = frappe.qb.DocType("Stock Ledger Entry")

		# actual qty is not up to date in case of backdated transaction
		last_sle_qty = (
			frappe.qb.from_(sle)
			.select(sle.qty_after_transaction)
			.where(
				(sle.item_code == args.get("item_code"))
				& (sle.warehouse == args.get("warehouse"))
				& (sle.is_cancelled == 0)
			)
			.orderby(CombineDatetime(sle.posting_date, sle.posting_time), order=Order.desc)
			.orderby(sle.creation, order=Order.desc)
			.limit(1)
			.run()
		)

		actual_qty = 0.0
		if last_sle_qty:
			actual_qty = last_sle_qty[0][0]
			
		ordered_qty = flt(bin_details.ordered_qty) + flt(args.get("ordered_qty"))
		reserved_qty = flt(bin_details.reserved_qty) + flt(args.get("reserved_qty"))
		indented_qty = flt(bin_details.indented_qty) + flt(args.get("indented_qty"))
		planned_qty = flt(bin_details.planned_qty) + flt(args.get("planned_qty"))

		# compute projected qty
		projected_qty = (
			flt(actual_qty)
			+ flt(ordered_qty)
			+ flt(indented_qty)
			+ flt(planned_qty)
			- flt(reserved_qty)
			- flt(bin_details.reserved_qty_for_production)
			- flt(bin_details.reserved_qty_for_sub_contract)
			- flt(bin_details.reserved_qty_for_production_plan)
		)

		frappe.db.set_value(
			"Bin",
			bin_name,
			{
				"actual_qty": actual_qty,
				"ordered_qty": ordered_qty,
				"reserved_qty": reserved_qty,
				"indented_qty": indented_qty,
				"planned_qty": planned_qty,
				"projected_qty": projected_qty,
				"stock_value": args.get("stock_value")
			},
			update_modified=True,
		)

	@frappe.whitelist()
	def on_cancel(self):
		self.flags.ignore_links = True
		company = frappe.get_doc("Company", self.company)
		tvr = self.calcluate_valuation_amount()
		self.cancel_stock_ledger_entry()
		self.set_sle_cancel()
		# self.update_stock_ledger()
		make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

	def cancel_stock_ledger_entry(self, ):
		for item in self.items:
			warehouse = item.warehouse or self.warehouse
			bin_name = get_or_make_bin(item.item_code, warehouse)

			bin_doc = frappe.get_doc("Bin", bin_name)
			prev_sle_doc = frappe.get_last_doc("Stock Ledger Entry", {"voucher_no": self.name, "item_code": item.item_code})
			
			sle_doc = frappe.new_doc("Stock Ledger Entry")
			sle_doc.item_code = item.item_code
			sle_doc.voucher_type = "Cash Invoice"
			sle_doc.voucher_no = self.name
			sle_doc.voucher_detail_no = item.name
			sle_doc.warehouse = item.warehouse or self.warehouse
			sle_doc.posting_time = self.posting_time
			sle_doc.posting_date = datetime.today()
			sle_doc.actual_qty = item.qty
			sle_doc.incoming_rate = item.rate
			sle_doc.stock_uom = frappe.db.get_value("Item", item.item_code, "stock_uom")
			sle_doc.company = self.company
			sle_doc.fiscal_year = self.validate_fiscal_year()
			sle_doc.is_cancelled = True
			sle_doc.serial_and_batch_bundle = ""
			sle_doc.save(ignore_permissions=True)
			sle_doc.submit()
			self.reverse_update_bin(bin_name, item)

	def reverse_update_bin(self, bin_name, item_data):
		bin_doc = frappe.get_doc("Bin", bin_name)
		bin_doc.actual_qty += item_data.get("qty")
		bin_doc.stock_value += bin_doc.valuation_rate * item_data.get("qty")
		bin_doc.save(ignore_permissions=True)

	
	def set_sle_cancel(self):
		frappe.db.sql(
			"""update `tabStock Ledger Entry` set is_cancelled=1,
			modified=%s, modified_by=%s
			where voucher_type=%s and voucher_no=%s and is_cancelled = 0""",
			(datetime.today(), frappe.session.user, self.doctype, self.name),
		)