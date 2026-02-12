<div align="center" markdown="1">

<img src="docs/images/logo.png" width="80" />


# WhatsApp Integration for Frappe Helpdesk

</div>


### WhatsApp Integration for Frappe Helpdesk

[![CI](https://github.com/Starktail/helpdesk_whatsapp/actions/workflows/ci.yml/badge.svg)](https://github.com/Starktail/helpdesk_whatsapp/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Starktail/helpdesk_whatsapp/graph/badge.svg?token=WM74TA5MO2)](https://codecov.io/gh/Starktail/helpdesk_whatsapp)

WhatsApp Integration for Frappe Helpdesk


### License

MIT


### Dependencies

- [Frappe](https://github.com/frappe/frappe)
- [frappe_whatsapp](https://github.com/shridarpatil/frappe_whatsapp)
- [Helpdesk](https://github.com/frappe/helpdesk)


### Screenshots

#### Helpdesk WhatsApp Settings

![alt text](docs/images/settings.png)

#### Helpdesk Ticket view

![alt text](docs/images/hd-ticket.png)

### Caveats

This app does not modify anything in the `helpdesk` Vue source (or dist) files, which means there are some limitations:
- On the Agent's ticket view, the **Source** field incorrectly shows as **Mail**
- At this time, the only way to Reply using WhatsApp is to use the **Reply** icon on a customer's message. Using the `✉️ Reply` button at the bottom of the page will not work, because it populates the "To" field with *Guest*

Ideally these would be solved by raising PR's against frappe/helpdesk that supports "external" communication channels

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench get-app https://github.com/shridarpatil/frappe_whatsapp.git
bench get-app helpdesk
bench install-app frappe_whatsapp
bench install-app helpdesk
bench install-app helpdesk_whatsapp
```

### Development

#### Tests

To run unit tests:

```shell
bench --site test_site run-tests --app helpdesk_whatsapp --coverage
```

To run UI/integration tests:

The following depencies are required
```shell
sudo apt update
# Dependencies for cypress: https://docs.cypress.io/guides/continuous-integration/introduction#UbuntuDebian
sudo apt-get install libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb

sudo apt-get install chromium
```

```shell
bench --site test_site run-ui-tests helpdesk_whatsapp --headless --browser chromium
```

#### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/helpdesk_whatsapp
pre-commit install

#(optional) Run against all the files
pre-commit run --all-files
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade


We use [Semgrep](https://semgrep.dev/docs/getting-started/) rules specific to [Frappe Framework](https://github.com/frappe/frappe)
```shell
# Install semgrep
python3 -m pip install semgrep

# Clone the rules repository
git clone --depth 1 https://github.com/frappe/semgrep-rules.git frappe-semgrep-rules

# Run semgrep specifying rules folder as config 
semgrep --config=/workspace/development/frappe-semgrep-rules/rules apps/helpdesk_whatsapp
```

#### Updating Documentation

For documentation, we use [vitepress](https://vitepress.dev/). You can run `yarn docs:dev` to preview the docs when applying changes

#### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request, as well as [Semgrep](https://semgrep.dev/docs/getting-started/)

