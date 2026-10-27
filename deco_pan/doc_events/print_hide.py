import types

from frappe.model import table_fields

from deco_pan.deco_pan.doctype.deco_pan_settings.deco_pan_settings import get_hidden_fields

LAYOUT_BREAKS = ("Section Break", "Tab Break")


def before_print(doc, method=None, print_settings=None):
	"""Keep fields hidden in Deco Pan Settings out of prints/PDFs for restricted users."""
	hidden = get_hidden_fields()
	if not hidden:
		return

	hide_fields(doc, hidden)
	for df in doc.meta.get_table_fields():
		for row in doc.get(df.fieldname) or []:
			hide_fields(row, hidden)


def hide_fields(doc, hidden):
	fieldnames = expand_layout_fields(doc.meta, hidden.get(doc.doctype))
	if not fieldnames:
		return

	# blank the values too, so custom print formats that reference them directly show nothing
	for fieldname in fieldnames:
		df = doc.meta.get_field(fieldname)
		if df and df.fieldtype not in LAYOUT_BREAKS and df.fieldtype != "Column Break":
			doc.set(fieldname, [] if df.fieldtype in table_fields else None)

	is_print_hide = doc.is_print_hide

	def _is_print_hide(self, fieldname, df=None, for_print=True):
		return fieldname in fieldnames or is_print_hide(fieldname, df, for_print)

	doc.is_print_hide = types.MethodType(_is_print_hide, doc)


def expand_layout_fields(meta, fieldnames):
	"""A hidden section or tab also hides every field inside it."""
	if not fieldnames:
		return set()

	result = set(fieldnames)
	hiding_until = None
	for df in meta.fields:
		if hiding_until and (
			df.fieldtype == "Tab Break" or (hiding_until == "Section Break" and df.fieldtype == "Section Break")
		):
			hiding_until = None
		if df.fieldname in fieldnames and df.fieldtype in LAYOUT_BREAKS:
			hiding_until = df.fieldtype
			continue
		if hiding_until:
			result.add(df.fieldname)
	return result
