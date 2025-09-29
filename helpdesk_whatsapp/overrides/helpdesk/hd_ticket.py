import frappe
from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import HDTicket


class CustomHDTicket(HDTicket):
	def send_acknowledgement_email(self):
		"""
		Override the send_acknowledgement_email method to prevent sending emails
		when a ticket is created via WhatsApp.
		"""
		# Do not send email for WhatsApp-created tickets
		if self.custom_whatsapp_mobile_number:
			return

		# Call the original method for other cases
		super().send_acknowledgement_email()

	@frappe.whitelist()
	def create_communication_via_contact(self, message, attachments=None, new_ticket=False):
		"""
		Override the create_communication_via_contact method to prevent sending emails
		when a ticket is created via WhatsApp.
		"""
		# Do not send email for WhatsApp-created tickets
		if self.custom_whatsapp_mobile_number:
			return

		# Call the original method for other cases
		super().create_communication_via_contact(
			message=message, attachments=attachments, new_ticket=new_ticket
		)

	def skip_email_workflow(self):
		"""
		Override the skip_email_workflow method to prevent sending emails for WhatsApp-created tickets.
		"""
		if self.custom_whatsapp_mobile_number:
			return True

		# Call the original method for other cases
		return super().skip_email_workflow()

	def on_communication_update(self, c):
		"""
		Override the on_communication_update method to handle guest users
		"""
		# =====================================================================================
		# Original code from hd_ticket.py
		# =====================================================================================
		# If communication is incoming, then it is a reply from customer, and ticket must
		# be reopened.
		if c.sent_or_received == "Received":
			self.status = "Open"
		# If communication is outgoing, it must be a reply from agent
		if c.sent_or_received == "Sent":
			# Set first response date if not set already
			self.first_responded_on = self.first_responded_on or frappe.utils.now_datetime()

			if frappe.db.get_single_value("HD Settings", "auto_update_status"):
				self.status = "Replied"

		# Fetch description from communication if not set already. This might not be needed
		# anymore as a communication is created when a ticket is created.
		self.description = self.description or c.content
		# Save the ticket, allowing for hooks to run.
		# self.save()
		# =====================================================================================
		# Custom code
		# =====================================================================================
		self.save(ignore_permissions=True)
		# =====================================================================================
