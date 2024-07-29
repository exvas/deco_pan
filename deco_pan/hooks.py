app_name = "deco_pan"
app_title = "Deco Pan"
app_publisher = "sammish"
app_description = "decopan"
app_email = "sammish.thundiyil@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/deco_pan/css/deco_pan.css"
# app_include_js = "/assets/deco_pan/js/deco_pan.js"

# include js, css files in header of web template
# web_include_css = "/assets/deco_pan/css/deco_pan.css"
# web_include_js = "/assets/deco_pan/js/deco_pan.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "deco_pan/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Purchase Invoice" : "public/js/purchase_invoice.js",
              "Purchase Order" : "public/js/purchase_order.js",
			  "Purchase Receipt" : "public/js/purchase_receipt.js",
			  "Sales Invoice" : "public/js/sales_invoice.js",
			  "Sales Order" : "public/js/sales_order.js",
			  "Delivery Note" : "public/js/delivery_note.js",
			  "Quotation" : "public/js/quotation.js",

}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "deco_pan/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "deco_pan.utils.jinja_methods",
# 	"filters": "deco_pan.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "deco_pan.install.before_install"
# after_install = "deco_pan.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "deco_pan.uninstall.before_uninstall"
# after_uninstall = "deco_pan.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "deco_pan.utils.before_app_install"
# after_app_install = "deco_pan.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "deco_pan.utils.before_app_uninstall"
# after_app_uninstall = "deco_pan.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "deco_pan.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events


doc_events = {
	

     "Purchase Invoice":{
                # "on_submit":"demo.doc_events.purchase_invoice.on_submit_se",

        
    },
	"Purchase Order":{

	},
	"Purchase Receipt":{

	},
	"Delivery Note":{

	},
	"Quotation":{

	},
	"Sales Order":{

	},
	"Sales Invoice":{

	},

    # "Expense Claim":{
    #     # "on_submit": "prago_tech.doc_events.expense_claim.on_submit"
    #     "on_submit":"prago_tech.doc_events.expense_claim.on_submit_se",
    #     "on_cancel":"prago_tech.doc_events.expense_claim.on_cancel_se",
    #     "before_submit":"prago_tech.doc_events.expense_claim.before_submit_se"

    # },

    # # "Sales Order":{
    # #     # "on_submit": "prago_tech.doc_events.expense_claim.on_submit"
    # #     "on_submit":"prago_tech.doc_events.sales_order.on_submit_se",
    # #     "on_cancel":"prago_tech.doc_events.sales_order.on_cancel_se"

    # # },

    # "Lead":{

    #     "validate":"prago_tech.doc_events.lead.validate",

    # },


   

}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"deco_pan.tasks.all"
# 	],
# 	"daily": [
# 		"deco_pan.tasks.daily"
# 	],
# 	"hourly": [
# 		"deco_pan.tasks.hourly"
# 	],
# 	"weekly": [
# 		"deco_pan.tasks.weekly"
# 	],
# 	"monthly": [
# 		"deco_pan.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "deco_pan.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "deco_pan.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "deco_pan.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["deco_pan.utils.before_request"]
# after_request = ["deco_pan.utils.after_request"]

# Job Events
# ----------
# before_job = ["deco_pan.utils.before_job"]
# after_job = ["deco_pan.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

fixtures =[
    {
	"doctype":"Custom Field",
	"filters":[
		["name","in",[
            "Sales Invoice Item-custom_ls_rate",
			"Sales Order Item-custom_ls_rate",
			"Quotation Item-custom_ls_rate",
			"Delivery Note Item-custom_ls_rate",
			"Purchase Order Item-custom_lp_rate",
			"Purchase Invoice Item-custom_lp_rate",
			"Purchase Receipt Item-custom_lp_rate",
 
					]]
	]
    
	},
    # {
    #     "doctype":"Property Setter",
	# 	"filters":[
	# 		["name","in",[
                
                
	
	# 		]]
	# ]
	# }
]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
report_override_html = {
	"Accounts Receivable": "overrides/reports/html/accounts_receivable.html",
}
report_override = {
	"Accounts Receivable": "deco_pan.overrides.reports.account_receivable.execute"
}
report_override_js = {
	"Accounts Receivable": "overrides/reports/js/accounts_receivable.js",
}

override_whitelisted_methods = {
	"frappe.desk.query_report.get_script": "deco_pan.overrides.report.get_script",
}
