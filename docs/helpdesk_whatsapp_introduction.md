# Introduction
## What is WhatsApp Integration for Frappe Helpdesk?

This is a [Frappe](https://frappeframework.com/) custom app, intended to add WhatsApp as a valid channel to use with [Frappe Helpdesk](https://github.com/frappe/helpdesk)

## Key Features


### Helpdesk WhatsApp Settings

![alt text](docs/images/settings.png)

### Helpdesk Ticket view

![alt text](docs/images/hd-ticket.png)

### Caveats

This app does not modify anything in the `helpdesk` Vue source (or dist) files, which means there are some limitations:
- On the Agent's ticket view, the **Source** field incorrectly shows as **Mail**
- At this time, the only way to Reply using WhatsApp is to use the **Reply** icon on a customer's message. Using the `✉️ Reply` button at the bottom of the page will not work, because it populates the "To" field with *Guest*

Ideally these would be solved by raising PR's against frappe/helpdesk that supports "external" communication channels

## Under the Hood

- [Frappe Framework](https://frappe.io/framework): A full-stack web application framework written in Python and Javascript. The framework provides a robust foundation for building web applications, including a database abstraction layer, user authentication, and a REST API.


## Installation

Go [here](https://github.com/Starktail/helpdesk_whatsapp) for installation.

## Support

- [Starktail Website](https://starktail.com)
- [Starktail Email Support](mailto:support@starktail.com)
- [Starktail WhatsApp Support](https://wa.me/27686318877?text=Hi%2C%20I%20have%20a%20question%20on%20WhatsApp%20Integration%20for%20Frappe%20Helpdesk)
