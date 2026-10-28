import re

import frappe
from frappe import _
from frappe.desk import query_report, reportview
from frappe.desk.query_report import get_column_as_dict

from deco_pan.deco_pan.doctype.deco_pan_settings.deco_pan_settings import (
	get_hidden_fields,
	get_report_restrictions,
)

_original_run = query_report.run
_original_get_form_params = reportview.get_form_params


def apply_patch():
	"""Route report data through the cost restrictions in Deco Pan Settings.

	Called on every request and background job: exports build their data via the
	module-level functions, so overriding only the endpoints is not enough.
	"""
	if query_report.run is not run:
		query_report.run = run
	if reportview.get_form_params is not get_form_params:
		reportview.get_form_params = get_form_params


# Query / Script reports


@frappe.whitelist()
def run(report_name, *args, **kwargs):
	hidden, blocked = get_report_restrictions()
	if not hidden and not blocked:
		return _original_run(report_name, *args, **kwargs)

	names = get_report_chain(report_name)
	if names & blocked:
		frappe.throw(_("You are not permitted to view this report."), frappe.PermissionError)

	result = _original_run(report_name, *args, **kwargs)
	# columns listed without a report apply to every report
	columns = set().union(*(hidden.get(name, set()) for name in names | {None}))
	if columns:
		strip_columns(result, columns)
	return result


def get_report_chain(report_name):
	"""The report and every report it is based on (custom reports can be based on custom reports)."""
	names = set()
	while report_name and report_name not in names:
		names.add(report_name)
		report_name = frappe.get_cached_value("Report", report_name, "reference_report")
	return names


def strip_columns(result, hidden_columns):
	drop = [
		i for i, col in enumerate(result.get("columns") or []) if get_column_as_dict(col).fieldname in hidden_columns
	]
	if not drop:
		return

	result["columns"] = [col for i, col in enumerate(result["columns"]) if i not in drop]

	rows = []
	for row in result.get("result") or []:
		if isinstance(row, dict):
			for fieldname in hidden_columns:
				row.pop(fieldname, None)
		elif isinstance(row, list | tuple):
			row = [value for i, value in enumerate(row) if i not in drop]
		rows.append(row)
	result["result"] = rows

	# charts and summary cards are usually built from the value columns
	result["chart"] = None
	result["report_summary"] = None


# Report view / Report Builder (list queries and their exports)


def get_form_params():
	data = _original_get_form_params()
	hidden = get_hidden_fields()
	if hidden and data.get("fields"):
		data.fields = [f for f in data.fields if not is_hidden_field(f, data.doctype, hidden)]
	return data


def is_hidden_field(field, doctype, hidden):
	field = field.replace("`", "")
	qualified = re.findall(r"tab([^.]+)\.(\w+)", field)
	if qualified:
		return any(fieldname in hidden.get(dt, ()) for dt, fieldname in qualified)

	fieldname = re.split(r"\s+as\s+", field.strip(), flags=re.I)[0].strip()
	return fieldname in hidden.get(doctype, ())
