import frappe
from frappe.utils import cint


def before_tests():
	frappe.clear_cache()
	# complete setup if missing
	from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

	print("Running before_tests")

	if not cint(frappe.db.get_single_value("System Settings", "setup_complete") or 0):
		print("Running setup_complete because company does not exist")
		setup_complete(
			{
				"language": "English",
				"email": "test@erpnext.com",
				"full_name": "Test User",
				"password": "test",
				"country": "South Africa",
				"timezone": "Africa/Johannesburg",
				"currency": "ZAR",
			}
		)

	frappe.db.commit()  # nosemgrep
