# Changelog

## 0.3.6
### Changed
- Hardened fetching logic for the NNGYK page: attempt secure TLS first, then gracefully fall back to an insecure (`ssl=False`) request only if certificate chain validation fails, ensuring data still refreshes.
- Stabilized HTML parsing for both **Minősítés** (Rating) and **Település** (Place) across multiple DOM variants.

### Fixed
- Update failures due to intermittent TLS certificate chain issues on the source site.

### Notes
- You may see a warning in logs: `Fetch with HA session failed … fallback to insecure ssl=False`. This is expected when the source site’s certificate chain is incomplete; the integration still refreshes data.
- If you have stale entities from earlier versions, remove them via UI.

## 0.3.5
– fix: add missing config_validation import in __init__.py

## 0.3.4
- First stable release
- Config flow (UI setup)
- One binary sensor per settlement, `device_class: problem`
- OFF (OK) if rating is "Megfelelő minőségű ivóvíz" or "Megfelelő, indikátor paraméterek miatt tűrhető minőségű ivóvíz"
- ON (PROBLEM) for any other rating or parsing error
- Hungarian attributes: Település, Minősítés, Forrás link, Lekérdezési időpont
- Automatic refresh twice a day (06:00 and 18:00, HA local timezone)
