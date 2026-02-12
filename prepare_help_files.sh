#!/bin/bash

# This is used in pacakge.json to block the help pages from public access, and copy the assets to the correct directory

AUTH_CONTENT="import frappe
from frappe import _

if frappe.session.user=='Guest':
    frappe.throw(_(\"You need to be logged in to access this page\"), frappe.PermissionError)"

for file in helpdesk_whatsapp/www/helpdesk_whatsapp_*.html; do
  if [ -f "$file" ]; then
    py_file="helpdesk_whatsapp/www/$(basename "$file" .html).py"
    echo "$AUTH_CONTENT" > "$py_file"
  fi
done

rm -rf ./helpdesk_whatsapp/public/chunks
mv ./helpdesk_whatsapp/www/assets/helpdesk_whatsapp/chunks ./helpdesk_whatsapp/public/.
mv ./helpdesk_whatsapp/www/assets/helpdesk_whatsapp/*.js ./helpdesk_whatsapp/public/.
mv ./helpdesk_whatsapp/www/assets/helpdesk_whatsapp/*.css ./helpdesk_whatsapp/public/.