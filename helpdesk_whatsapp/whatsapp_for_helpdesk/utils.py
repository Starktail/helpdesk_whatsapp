import frappe
from frappe.utils.fixtures import sync_fixtures


def after_install():
	"""
	This function is called after the app is installed.
	It can be used to perform any setup tasks required by the app.
	"""
	# Sync fixtures to ensure that the custom field `custom_whatsapp_mobile_number` has been updated
	sync_fixtures("helpdesk_whatsapp")

	# Update the "Default" HD Ticket Template to include the WhatsApp Message field
	template = frappe.get_doc("HD Ticket Template", "Default")
	if "custom_whatsapp_mobile_number" not in [field.fieldname for field in template.fields]:
		template.append(
			"fields",
			{"fieldname": "custom_whatsapp_mobile_number"},
		)
		template.save()
		frappe.db.commit()  # nosemgrep: frappe-manual-commit
