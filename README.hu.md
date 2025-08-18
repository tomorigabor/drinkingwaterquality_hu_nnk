# Drinking Water Quality HU (NNGYK)

Home Assistant egyedi integráció az NNGYK "Magyarországi települések ivóvízminősége" nyilvános oldalához.
Településenként egy **bináris szenzort** hoz létre, amely **OK/PROBLÉMA** állapotban jelzi a minősítést.

> Nem hivatalos projekt. Csak publikus weboldalt olvas; nem kér bejelentkezést vagy tokent, és nem áll kapcsolatban az NNGYK-val.

## Funkciók
- UI-ból konfigurálható
- Településenként 1 db `binary_sensor`
- OFF (OK), ha a minősítés:
  - "Megfelelő minőségű ivóvíz"
  - "Megfelelő, indikátor paraméterek miatt tűrhető minőségű ivóvíz"
- ON (PROBLÉMA) minden más minősítés vagy parszolási hiba esetén
- Attribútumok (magyarul):
  - Település
  - Minősítés
  - Forrás link
  - Lekérdezési időpont
- Automatikus frissítés naponta kétszer: 06:00 és 18:00 (HA helyi időzónája szerint)

## Telepítés (HACS – ajánlott)
1. HACS → Integrations → jobb felső menü (⋮) → Custom repositories
2. Add meg a repo URL-jét, válaszd a Category: Integration opciót, majd Add
3. Telepítsd a listából a "Drinking Water Quality HU" integrációt
4. Indítsd újra a Home Assistantot

### Újraindítás után: integráció hozzáadása
- Menj ide: Settings → Devices & Services → Add Integration
- Keresd: "Drinking Water Quality HU", kattints rá
- Egyetlen mezőt kér: "Település ID"

### Hogyan találsz Település ID-t
1. Nyisd meg ezt az oldalt: https://www.nnk.gov.hu/index.php/kornyezetegugy/kornyezetegeszsegugyi-laboratoriumi-osztaly/vizhigienes-laboratorium/ivoviz/magyarorszagi-telepulesek-ivovizminosege.html
2. Keresd ki a települést, majd kattints a nevére
3. A megnyíló oldal URL-jéből másold ki az "&id=" utáni számot (példa: ...?view=placemark&id=XXXXX → XXXXX)
4. Illeszd be a "Település ID" mezőbe, majd küldd el

### Mi történik ezután
- Létrejön egy `binary_sensor.ivoviz_<telepules_slug>` entitás
- Az első lekérdezés azonnal lefut; a nevek "Ivóvíz — <Település>" formátumra állnak
- Állapot: a két "megfelelő" minősítésnél OFF (OK), más esetben ON (PROBLÉMA)
- Attribútumok kitöltve; a frissítés 06:00 és 18:00 órakor fut naponta

## Entitások
- Bináris szenzor
  - Entity ID: `binary_sensor.ivoviz_<telepules_slug>`
  - Név: Ivóvíz — <Település>
  - Állapot:
    - off = OK
    - on = PROBLÉMA
  - Attribútumok:
    - Település, Minősítés, Forrás link, Lekérdezési időpont

## Ütemezés
- Napi kétszer 06:00 és 18:00
- Futás után automatikusan azonnal a következő időpontra ütemez

## Jogi
- Nem hivatalos, nem áll kapcsolatban az NNGYK-val
- A logók és védjegyek a tulajdonosaiké
- Az adatok a fenti publikus oldalról származnak

## Közreműködés
- Hibajegyek és PR-ek szívesen fogadva; a HACS és hassfest ellenőrzéseket tartsd zölden

## Licenc
MIT – lásd: `LICENSE`
