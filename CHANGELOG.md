# Changelog

## 0.3.4
- First stable release
- Config flow (UI setup)
- One binary sensor per settlement, `device_class: problem`
- OFF (OK) if rating is "Megfelelő minőségű ivóvíz" or "Megfelelő, indikátor paraméterek miatt tűrhető minőségű ivóvíz"
- ON (PROBLEM) for any other rating or parsing error
- Hungarian attributes: Település, Minősítés, Forrás link, Lekérdezési időpont
- Automatic refresh twice a day (06:00 and 18:00, HA local timezone)
