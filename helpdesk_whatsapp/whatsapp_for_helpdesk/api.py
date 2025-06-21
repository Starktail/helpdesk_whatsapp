import frappe

from helpdesk_whatsapp.whatsapp_for_helpdesk.html_formatter import html_to_whatsapp


def create_outgoing_whatsapp_message(doc, method=None):
	"""
	Intended to be called from a Communication document
	"""

	if doc.doctype != "Communication":
		return

	if doc.communication_medium != "Other":
		return

	# Create WhatsApp message
	wa_message = frappe.new_doc("WhatsApp Message")
	wa_message.to = doc.recipients
	wa_message.message_type = "Manual"
	wa_message.message = format_content(doc.content)

	# Set status to queued
	wa_message.status = "Queued"
	try:
		wa_message.insert(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(message=str(e), title="Failed to create WhatsApp Message from Communication")


def format_content(html: str) -> str:
	"""
	Format the content for WhatsApp.
	"""
	# We use the selector to only process the content inside the 'ql-editor' div
	return html_to_whatsapp(html, selector=".ql-editor")
