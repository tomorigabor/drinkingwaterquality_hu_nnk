# Drinking Water Quality HU (NNGYK)

Home Assistant custom integration for the Hungarian National Public Health and Pharmaceutical Center (NNGYK) public page "Drinking water quality of Hungarian settlements".
It creates one **binary sensor** per settlement that reports **OK/PROBLEM** based on the current rating.

> Unofficial project. This integration only parses a public web page; it requires no tokens or login and is not affiliated with NNGYK.

[Olvasd magyarul](./README.hu.md)

## Features
- Configurable from the UI (config flow)
- One `binary_sensor` per settlement with `device_class: problem`
- OFF (OK) if the rating is either:
  - "Megfelelo minosegu ivoviz"
  - "Megfelelo, indikator parameterek miatt turheto minosegu ivoviz"
- ON (PROBLEM) for any other rating or parsing error
- Attributes (kept in Hungarian to match the source):
  - Település (Settlement)
  - Minősítés (Rating)
  - Forrás link (Source link)
  - Lekérdezési időpont (Fetched at)
- Automatic updates twice a day: 06:00 and 18:00 (Home Assistant local timezone)

## Installation (HACS – recommended)
1. HACS → Integrations → top-right menu (⋮) → Custom repositories
2. Add your repository URL, choose Category: Integration, then Add
3. Install "Drinking Water Quality HU" from the list
4. Restart Home Assistant

### After restart: add the integration
- Go to Settings → Devices & Services → Add Integration
- Search for "Drinking Water Quality HU" and click it
- A form appears with one field: "Placemark ID"

### How to find the Placemark ID
1. Open this page: https://www.nnk.gov.hu/index.php/kornyezetegugy/kornyezetegeszsegugyi-laboratoriumi-osztaly/vizhigienes-laboratorium/ivoviz/magyarorszagi-telepulesek-ivovizminosege.html
2. Find your settlement and click its name
3. In the opened page URL, copy the number after "&id=" (example: ...?view=placemark&id=XXXXX → XXXXX)
4. Paste that number into the "Placemark ID" field and submit

### What happens next
- An entity like `binary_sensor.ivoviz_<settlement_slug>` is created
- The first fetch runs immediately; names become "Ivóvíz — <Settlement>"
- State is OFF for the two "OK" ratings above; ON otherwise
- Attributes are populated; periodic refresh runs at 06:00 and 18:00 daily

## Entities
- Binary sensor
  - Entity ID: `binary_sensor.ivoviz_<settlement_slug>`
  - Friendly name: Ivóvíz — <Settlement>
  - State:
    - off = OK (two accepted ratings)
    - on  = PROBLEM (anything else or parsing error)
  - Attributes:
    - Település, Minősítés, Forrás link, Lekérdezési időpont

## Update schedule
- Twice daily at 06:00 and 18:00 (HA local timezone)
- After each run it reschedules itself; after HA restarts it schedules the next boundary automatically

## Privacy & Legal
- Not affiliated with NNGYK. Logos and trademarks belong to their owners
- Data is parsed from the public page above; if the page layout changes, parsing may need updates

## Contributing
- Issues and PRs welcome. Please keep HACS and hassfest checks green

## License
MIT — see `LICENSE`
