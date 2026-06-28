import time
import traceback

import frappe
from bs4 import BeautifulSoup
from helpdesk.utils import publish_event

from helpdesk_whatsapp.whatsapp_for_helpdesk.html_formatter import html_to_whatsapp


def create_outgoing_whatsapp_message(doc, method):
	"""
	Intended to be called from a hook on a Communication document
	"""

	if doc.doctype != "Communication":
		return

	if doc.communication_medium != "":
		return

	if doc.sent_or_received != "Sent":
		return

	if doc.custom_whatsapp_message_sent:
		return

	# We expect the recipient to be a WhatsApp number in E.164 form without the
	# leading '+', e.g. '27825678901'.
	recipient = (doc.recipients or "").strip()
	if not recipient.isdigit() or not (8 <= len(recipient) <= 15):
		frappe.log_error(
			message=f"Invalid WhatsApp number ({doc.recipients}) on Communication {doc.name}",
			title="WhatsApp Message Creation Error",
		)
		frappe.db.set_value("Communication", doc.name, "delivery_status", "Error", update_modified=False)
		if doc.reference_doctype == "HD Ticket":
			publish_event("helpdesk:ticket-update", doc.reference_name)
		return

	# If this outgoing communication is 24 hours after the last WhatsApp message,
	# we need to use a template message and can not send a free-form message.
	cut_off_time = frappe.utils.add_to_date(frappe.utils.now(), hours=-24)
	content = format_content(doc.content)
	message = (content[:800] + "...") if len(content) > 800 else content  # adhere to WhatsApp character limit

	last_whatsapp_messages = frappe.get_all(
		"WhatsApp Message",
		filters={
			"from": doc.recipients,
			"type": "Incoming",
			"creation": [">", cut_off_time],
		},
		order_by="creation desc",
		limit=1,
	)
	if not last_whatsapp_messages:
		# Create a new WhatsApp Message based on a template
		settings = frappe.get_cached_doc("Helpdesk WhatsApp Settings")
		template = settings.whastapp_template_for_ticket_replies
		wa_message = frappe.new_doc("WhatsApp Message")
		wa_message.type = "Outgoing"
		wa_message.to = doc.recipients
		wa_message.message_type = "Template"
		wa_message.template = template

		# Set our context variables for the template
		wa_message.flags.custom_ref_doc = {
			"ticket_name": doc.reference_name,
			"reply_content": message,
		}
		wa_message.reference_doctype = "Communication"
		wa_message.reference_name = doc.name

	else:
		# Create free-form WhatsApp message
		wa_message = frappe.new_doc("WhatsApp Message")
		wa_message.type = "Outgoing"
		wa_message.to = doc.recipients
		wa_message.message_type = "Manual"
		wa_message.message = format_content(doc.content)
		wa_message.reference_doctype = "Communication"
		wa_message.reference_name = doc.name

		# Handle attachments
		soup = BeautifulSoup(doc.content, "html.parser")
		img_tag = soup.find("img")
		video_tag = soup.find("video")

		if img_tag and img_tag.get("src"):
			wa_message.content_type = "image"
			wa_message.attach = img_tag.get("src")
		elif video_tag and video_tag.get("src"):
			wa_message.content_type = "video"
			wa_message.attach = video_tag.get("src")

	# Set status to queued
	wa_message.status = "Queued"
	try:
		wa_message.insert(ignore_permissions=True)
		frappe.enqueue(mark_communication_as_sent, doc=doc)
	except Exception as e:
		frappe.log_error(
			message="".join(traceback.format_exception(e)),
			title="Failed to create WhatsApp Message from Communication",
		)
		frappe.db.set_value("Communication", doc.name, "delivery_status", "Error", update_modified=False)
		if doc.reference_doctype == "HD Ticket":
			publish_event("helpdesk:ticket-update", doc.reference_name)
		raise e


def enqueue_create_incoming_communication(doc, method):
	"""
	Intended to be called from a hook on a WhatsApp Message
	"""
	frappe.enqueue(method=create_incoming_communication, enqueue_after_commit=True, doc=doc)


def create_incoming_communication(doc):
	# Wait for a few seconds, just in case an attachment is added after insert of Whatsapp Message
	time.sleep(5)

	if doc.doctype != "WhatsApp Message":
		return

	if doc.type != "Incoming":
		return

	# Determine if this is a new ticket or a reply to an existing one
	# Later we can use LLMs to analyze the message content and decide
	# For now, get the timer setting and check if this message is within the timeout period
	settings = frappe.get_cached_doc("Helpdesk WhatsApp Settings")
	cut_off_time = frappe.utils.add_to_date(frappe.utils.now(), seconds=-int(settings.chat_to_ticket_timeout))
	subject = (doc.message[:20] + "...") if len(doc.message) > 20 else doc.message

	last_whatsapp_messages = frappe.get_all(
		"WhatsApp Message",
		filters={
			"from": doc.get("from"),
			"type": "Incoming",
			"creation": [">", cut_off_time],
			"name": ["!=", doc.name],
			"reference_doctype": "Communication",
		},
		fields=["name", "reference_name"],
		order_by="creation desc",
		limit=1,
	)
	if not last_whatsapp_messages:
		last_outgoing_whatsapp_messages = frappe.get_all(
			"WhatsApp Message",
			filters={
				"to": doc.get("from"),
				"type": "Outgoing",
				"creation": [">", cut_off_time],
				"reference_doctype": "Communication",
			},
			fields=["name", "reference_name"],
			order_by="creation desc",
			limit=1,
		)
		last_whatsapp_messages += last_outgoing_whatsapp_messages
	if last_whatsapp_messages:
		last_whatsapp_message = last_whatsapp_messages[0]
		last_communication = (
			frappe.get_doc("Communication", last_whatsapp_message.reference_name)
			if last_whatsapp_message
			else None
		)
		ticket_name = last_communication.reference_name if last_communication else None

		# Validate if the ticket is merged to find the correct ticket
		if ticket_name:
			ticket_name = check_for_merges_and_get_latest_ticket(ticket_name)

	else:
		# Else, we create a new ticket
		ticket = frappe.get_doc(
			{
				"doctype": "HD Ticket",
				"subject": subject,
				"description": doc.message,
				"custom_whatsapp_mobile_number": doc.get("from"),
				"contact": get_contact_from_whatsapp_number(doc.get("from")),
			}
		)
		ticket.insert(ignore_permissions=True)
		ticket_name = ticket.name

	message = doc.message

	# If the WhatsApp message has an attachment, embed this in the the communication content
	if doc.attach:
		if doc.content_type == "image":
			message += f'<br><img src="{doc.attach}"></img><br><a href="{doc.attach}" target="_blank"> Download image </a>'
		elif doc.content_type == "audio":
			message += f'<audio controls src="{doc.attach}"></audio><br><a href="{doc.attach}" target="_blank"> Download audio </a>'
		elif doc.content_type == "video":
			message += f"""
				<video controls width="250">
				<source src="{doc.attach}" />
				<br>
				<a href="{doc.attach}" target="_blank"> Download video </a>
				</video>
			"""
		else:
			message += f'<a href="{doc.attach}" target="_blank"> Link to file </a>'

	communication = frappe.get_doc(
		{
			"communication_medium": "",
			"communication_type": "Automated Message",
			"content": message,
			"doctype": "Communication",
			"email_account": None,
			"recipients": doc.get("from"),
			"reference_doctype": "HD Ticket",
			"reference_name": ticket_name,
			"sent_or_received": "Received",
			"status": "Linked",
			"subject": subject,
		}
	)

	# if last_communication and last_communication.message_id:
	# 	communication.in_reply_to = last_communication.name

	communication.insert(ignore_permissions=True)
	frappe.enqueue(
		link_communication_to_whatsapp_message,
		whatsapp_message_name=doc.name,
		communication_name=communication.name,
	)


def update_communication(doc, method):
	"""
	Intended to be called from an on_update hook on WhatsApp Message
	"""
	if doc.doctype != "WhatsApp Message":
		return

	if doc.type != "Outgoing":
		return

	try:
		if doc._doc_before_save:
			if doc._doc_before_save.status != doc.status and doc.status in ["delivered", "read"]:
				if doc.reference_doctype == "Communication":
					communication = frappe.get_doc("Communication", doc.reference_name)
					if doc.status == "read":
						frappe.db.set_value("Communication", doc.reference_name, "delivery_status", "Sent")
						if communication.reference_doctype == "HD Ticket":
							publish_event("helpdesk:ticket-update", communication.reference_name)
					if doc.status == "delivered":
						frappe.db.set_value("Communication", doc.reference_name, "delivery_status", "Read")
						if communication.reference_doctype == "HD Ticket":
							publish_event("helpdesk:ticket-update", communication.reference_name)
	except Exception as e:
		frappe.log_error(
			message="".join(traceback.format_exception(e)),
			title="Failed to update Communication from WhatsApp Message status change",
		)


def format_content(html: str) -> str:
	"""
	Format the content for WhatsApp.
	"""
	# We use the selector to only process the content inside the 'ql-editor' div
	return html_to_whatsapp(html, selector=".ql-editor")


def link_communication_to_whatsapp_message(
	whatsapp_message_name: str, communication_name: str, retries: int = 0
):
	"""
	Link a WhatsApp Message to a Communication document.
	"""
	whatsapp_message = frappe.get_doc("WhatsApp Message", whatsapp_message_name)

	if whatsapp_message:
		whatsapp_message.reference_doctype = "Communication"
		whatsapp_message.reference_name = communication_name
		whatsapp_message.save(ignore_permissions=True)
	else:
		if retries < 5:
			# Retry linking after a short delay
			frappe.enqueue(
				link_communication_to_whatsapp_message,
				whatsapp_message_name=whatsapp_message_name,
				communication_name=communication_name,
				retries=retries + 1,
				queue="long",
			)
			return
		else:
			frappe.log_error(
				message=f"Failed to link WhatsApp Message {whatsapp_message_name} to Communication {communication_name} after {retries} retries.",
				title="Linking Error",
			)


def get_contact_from_whatsapp_number(number: str):
	"""
	Get the contact from a WhatsApp number.
	"""
	number = number.strip()
	if not number.startswith("+"):
		number = f"+{number}"

	contact_phone_nos = frappe.get_all(
		"Contact Phone",
		filters={
			"parenttype": "Contact",
			"phone": number,
		},
		fields=["parent"],
	)

	if contact_phone_nos:
		return contact_phone_nos[0].parent

	return None


def mark_communication_as_sent(doc):
	"""
	Mark the Communication document as sent.
	"""
	frappe.db.set_value(
		"Communication", doc.name, "custom_whatsapp_message_sent", True, update_modified=False
	)
	frappe.db.set_value("Communication", doc.name, "delivery_status", "Sending", update_modified=False)
	if doc.reference_doctype == "HD Ticket":
		publish_event("helpdesk:ticket-update", doc.reference_name)


def check_for_merges_and_get_latest_ticket(ticket_name: str) -> str:
	"""
	Recursively check for merged tickets and return the latest ticket name.
	"""
	found_latest = False
	while not found_latest:
		ticket = frappe.get_doc("HD Ticket", ticket_name)
		if ticket.is_merged:
			ticket_name = ticket.merged_with
		else:
			found_latest = True
	return ticket_name
