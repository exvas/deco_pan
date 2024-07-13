// Copyright (c) 2024, sammish and contributors
// For license information, please see license.txt

frappe.ui.form.on("Cash Invoice", {
	cancel(frm){
		frappe.call({
			doc:frm.doc,
			method: "cancel_doc"
		})
	},

	refresh(frm){
		if(frm.doc.docstatus != 0){
			frm.add_custom_button(
				__("Accounting Ledger"),
				function () {
					frappe.route_options = {
						voucher_no: frm.doc.name,
						from_date: frm.doc.date,
						to_date: moment(frm.doc.modified).format("YYYY-MM-DD"),
						company: frm.doc.company,
						group_by: "Group by Voucher (Consolidated)",
						show_cancelled_entries: frm.doc.docstatus === 2,
					};
					frappe.set_route("query-report", "General Ledger");
				},
				__("View")
			);

			frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.date,
					to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
					company: frm.doc.company,
					show_cancelled_entries: frm.doc.docstatus === 2,
					ignore_prepared_report: true
				};
				frappe.set_route("query-report", "Stock Ledger");
			}, __("View"));
		}
	},
	onload(frm){
		frm.ignore_doctypes_on_cancel_all = ["GL Entry", "Stock Ledger Entry"];
        if(frm.doc.__islocal){
            frappe.db.get_doc("Deco Pan Settings").then(data=>{
				if(!data.default_cost_center || !data.default_income_account){
					frappe.throw("Please setup Deco Pan Settings");
					frm.disable_save();
				}
                frm.set_value("cost_center", data.default_cost_center)
                frm.set_value("payment_mode", data.payment_mode)
                frm.set_value("warehouse", data.default_warehouse)
                frm.set_value("company", frappe.defaults.get_user_default("Company"))
				
            });
        }
        frm.set_query("cost_center", function () {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0
				},
			};
		});
		frm.set_query("warehouse", function () {
			return {
				filters: {
					company: frm.doc.company,
				},
			};
		});
        frm.fields_dict["items"].grid.get_field("item_code").get_query = function () {
			return {
				filters: {
					disabled: 0
				},
			};
		};
		frm.fields_dict["items"].grid.get_field("income_account").get_query = function () {
			return {
				filters: {
					company: frm.doc.company,
					is_group: 0
				},
			};
		};
		frm.fields_dict["items"].grid.get_field("warehouse").get_query = function () {
			return {
				filters: {
					company: frm.doc.company
				},
			};
		};
    },
	additional_discount_amount(frm){
		let discountAmount = frm.doc.total - frm.doc.additional_discount_amount;
		console.log(discountAmount)
		frm.set_value("net_total", discountAmount);
		frm.set_value("grand_total", discountAmount);
		frm.trigger("set_rounded_total");
	},
	calculate_totals(frm){
		let total = 0;
		frm.doc.items.forEach(item=>{
			total += item.amount;
		});
		let adm = frm.doc.additional_discount_amount || 0;
		let net_total = total - adm
		frm.set_value("total", total);
		frm.set_value("net_total", net_total);
		frm.set_value("rounded_total", net_total);
		frm.set_value("grand_total", net_total);
		frm.trigger("set_rounded_total");
	},
	set_rounded_total(frm) {
		var disable_rounded_total = 0;
		if(frappe.meta.get_docfield(frm.doc.doctype, "disable_rounded_total", frm.doc.name)) {
			disable_rounded_total = frm.doc.disable_rounded_total;
		} else if (frappe.sys_defaults.disable_rounded_total) {
			disable_rounded_total = frappe.sys_defaults.disable_rounded_total;
		}

		if (cint(disable_rounded_total)) {
			frm.set_value("rounded_total", 0);
			return;
		}

		if(frappe.meta.get_docfield(frm.doc.doctype, "rounded_total", frm.doc.name)) {
			let rounded_total = round_based_on_smallest_currency_fraction(frm.doc.grand_total,
				"INR", precision("rounded_total"));
			frm.doc.rounded_total = rounded_total;
		}
	},
	disable_rounded_total(frm){
		frm.trigger("set_rounded_total");
	},
	validate(frm){
		if(frm.doc.items.length == 0){
			frappe.throw("Add atleast one item!")
		}
		let gt = frm.doc.rounded_total || frm.doc.grand_total
		frm.set_value("paid_amount", gt)
		let total_qty = 0
		frm.doc.items.forEach(row=>{
			if(row.available_qty <= 0){
				frappe.throw(`${row.item_code} require ${row.qty} qty in ${frm.doc.warehouse}`)
			}
			total_qty += row.qty;
			frappe.db.get_doc("Deco Pan Settings").then(data=>{
				row.cost_center = frm.doc.cost_center || data.default_cost_center;
				row.income_account = data.default_income_account;
				row.warehouse = frm.doc.warehouse || data.default_warehouse;
				frm.refresh_field("items");
			});
		})
		frm.trigger("calculate_totals");
		frm.set_value("total_quantity", total_qty);
		frm.set_value("paid_amount", frm.doc.rounded_total || frm.doc.grand_total);
	},
	set_pos_data(frm) {
		let company = frm.doc.company || frappe.defaults.get_user_default("Company")
		if (!company) {
			frappe.throw(__("Could not find a company for transaction!"));
		} else {
			frm.call({
				doc: frm.doc,
				method: "set_missing_values",
				callback: function (r) {
					if (!r.exc) {
					}
				},
			});
		}
	},
	warehouse(frm){
		frm.doc.items.forEach(row=>{
			if(frm.doc.warehouse){
				frappe.call({
					method: "get_stock_details",
					async: false,
					freeze: true,
					freeze_message: "Calculating available stock...",
					doc: frm.doc,
					args:{},
					callback:function(r){
						if(r.message){
							console.log(r.message)
							row.warehouse = frm.doc.warehouse;
							row.available_qty = r.message.actual_qty;
						}
						frm.refresh_field("items");
					}
				});
			}
		})
	}
});

frappe.ui.form.on("Cash Invoice Item", {
	items_add(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		frappe.db.get_doc("Deco Pan Settings").then(data=>{
			row.cost_center = data.default_cost_center;
			row.income_account = data.default_income_account;
			row.warehouse = data.default_warehouse;
			frm.refresh_field("items");
		});
	},
	item_code(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		if(row.item_code){
			frappe.call({
				method: "erpnext.stock.get_item_details.get_item_details",
				async: false,
				args:{
					doc: frm.doc,
					args: {
						item_code: row.item_code,
						barcode: null,
						customer: frm.doc.customer,
						currency: "INR",
						update_stock: 0,
						conversion_rate: 1,
						price_list: "Standard Selling",
						price_list_currency: "INR",
						plc_conversion_rate: 1,
						company: frm.doc.company || frappe.defaults.get_user_default("Company"),
						is_pos: 1,
						is_return: 0,
						// ignore_pricing_rule: 0,
						doctype: frm.doc.doctype,
						name: frm.doc.name,
						qty: row.qty,
						net_rate: 0,
						base_net_rate: 0,
						stock_qty: 1,
						weight_uom: "",
						stock_uom: row.uom,
						pos_profile: "",
						cost_center: row.cost_center || frm.doc.cost_center,
						tax_category: "",
						child_doctype: row.name,
						child_docname: row.name,
						update_stock: 1,
						warehouse: frm.doc.warehouse || row.warehouse
					}
				},
				callback:function(r){
					if(r.message){
						row.rate = r.message.price_list_rate;
						row.amount = r.message.price_list_rate * row.qty;
						row.warehouse = frm.doc.warehouse;
					}
					// frm.refresh_field("items");
				}
			});
			if(frm.doc.warehouse){
				frappe.call({
					method: "get_stock_details",
					async: true,
					freeze: true,
					freeze_message: "Calculating available stock...",
					doc: frm.doc,
					args:{},
					callback:function(r){
						if(r.message){
							console.log(r.message)
							row.warehouse = frm.doc.warehouse;
							row.available_qty = r.message.actual_qty;
						}
						frm.refresh_field("items");
					}
				});
			}
		}
		frm.trigger("calculate_totals");

	},
	qty:function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		if(row.qty < 1){
			frappe.throw(_(`Qty cannot be less than 1 for ${row.item_code}`));
		}else if(row.qty > row.available_qty){
			frappe.throw(_(`Qty cannot be greater than ${row.available_qty} for ${row.item_code}`));
		}
		row.amount = row.qty * row.rate;
		frm.refresh_field("items");
		frm.trigger("calculate_totals");
	},
	rate:function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.rate;
		frm.refresh_field("items");
		frm.trigger("calculate_totals");
	}
});
