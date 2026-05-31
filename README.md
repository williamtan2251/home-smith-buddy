# Home Smith Buddy

A [Home Assistant](https://www.home-assistant.io/) custom integration (installable
via [HACS](https://hacs.xyz/)) that lets any Home Assistant user file a support
**ticket to the admin**. Tickets are submitted from a dedicated sidebar panel and
delivered to the admin by **email (SMTP)**.

## Features

- **Sidebar panel** — a "Log a Ticket" form (subject, priority, message) available
  to every logged-in user.
- **Email delivery** — tickets are emailed to a configured admin address over SMTP
  (plain, STARTTLS, or TLS).
- **Service** — `home_smith_buddy.create_ticket` so automations and scripts can
  raise tickets too.
- **UI setup** — SMTP settings are entered through Home Assistant's config flow,
  with a connection test, and can be changed later via *Reconfigure*.

## Installation (HACS)

1. In HACS → **Integrations** → ⋮ → **Custom repositories**, add this repository
   as an *Integration*.
2. Install **Home Smith Buddy** and restart Home Assistant.
3. **Settings → Devices & Services → Add Integration → Home Smith Buddy** and fill
   in your SMTP details.

> Manual install: copy `custom_components/home_smith_buddy/` into your Home
> Assistant `config/custom_components/` directory and restart.

## Configuration

| Field        | Notes                                              |
| ------------ | -------------------------------------------------- |
| SMTP host    | e.g. `smtp.gmail.com`                              |
| SMTP port    | `587` for STARTTLS, `465` for TLS, `25` for plain |
| Username     | Optional — leave blank for unauthenticated relays |
| Password     | Optional                                           |
| From address | The envelope/sender address                        |
| Recipient    | The admin address tickets are sent to             |
| Encryption   | `none`, `starttls`, or `tls`                       |

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements_test.txt
pytest          # run tests
ruff check .    # lint
```

## License

MIT — see [LICENSE](LICENSE).
