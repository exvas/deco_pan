import frappe
from frappe import _
from frappe.desk import query_report
from frappe.desk.query_report import get_column_as_dict

from deco_pan.deco_pan.doctype.deco_pan_settings.deco_pan_settings import get_report_restrictions

_original_run = query_report.run


def apply_patch():
	"""Route query report runs (screen and export) through `run` below.

	Called on every request and background job: export builds its data via the
	module-level `query_report.run`, so overriding only the endpoint is not enough.
	"""
	if query_report.run is not run:
		query_report.run = run


@frappe.whitelist()
def run(report_name, *args, **kwargs):
	hidden, blocked = get_report_restrictions()
	if not hidden and not blocked:
		return _original_run(report_name, *args, **kwargs)

	names = {report_name, frappe.get_cached_value("Report", report_name, "reference_report")}
	if names & blocked:
		frappe.throw(_("You are not permitted to view this report."), frappe.PermissionError)

	result = _original_run(report_name, *args, **kwargs)
	columns = set().union(*(hidden.get(name, set()) for name in names))
	if columns:
		strip_columns(result, columns)
	return result


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
