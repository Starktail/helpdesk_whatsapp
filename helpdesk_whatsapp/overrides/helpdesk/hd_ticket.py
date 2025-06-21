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

	def create_communication_via_contact(self, message, attachments=None, new_ticket=False):
		"""
		Override the create_communication_via_contact method to prevent sending emails
		when a ticket is created via WhatsApp.
		"""
		# Do not send email for WhatsApp-created tickets
		if self.custom_whatsapp_mobile_number:
			return

		# Call the original method for other cases
		super().create_communication_via_contact(message=message, attachments=message, new_ticket=message)
