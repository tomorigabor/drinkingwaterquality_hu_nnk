from __future__ import annotations

from datetime import datetime as dt_datetime, time as dt_time, timedelta as dt_timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .const import DOMAIN, PLATFORMS
from .coordinator import NNKCoordinator

# A HA validátora miatt – nincs yaml-os beállítás, csak config entry.
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up domain namespace."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    placemark_id = int(entry.data["placemark_id"])

    coord = NNKCoordinator(hass, placemark_id)
    # Első frissítés – ekkor már tudjuk a település nevét (ha elérhető).
    await coord.async_config_entry_first_refresh()

    # Config entry címének átírása településnévre
    place = (coord.data.place_name or "").strip() if coord.data else ""
    if place:
        hass.config_entries.async_update_entry(entry, title=place)

    # DEVICE ÁTNEVEZÉSE: a régóta zavaró "Placemark" helyett "Ivóvíz — <település>"
    try:
        devreg = dr.async_get(hass)
        for dev in dr.async_entries_for_config_entry(devreg, entry.entry_id):
            devreg.async_update_device(
                dev.id,
                name=f"Ivóvíz — {place or 'Település'}",
                manufacturer="NNGYK",
                model="Ivóvíz minőség",
            )
    except Exception:
        # Ne akadályozza a betöltést, ha valamiért nem sikerül átnevezni.
        pass

    # A koordinátort és az időzítőt eltároljuk
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coord, "timer_unsub": None}
    store = hass.data[DOMAIN][entry.entry_id]

    async def _do_refresh(_now) -> None:
        await coord.async_request_refresh()
        _schedule_next()

    def _next_boundary(now_utc: dt_datetime) -> dt_datetime:
        """Következő 06:00 vagy 18:00 helyi időpont UTC-ben."""
        local_now = dt_util.as_local(now_utc)
        today = local_now.date()
        tz = dt_util.get_time_zone(hass.config.time_zone)

        six_local = dt_datetime.combine(today, dt_time(6, 0, 0, tzinfo=tz))
        eighteen_local = dt_datetime.combine(today, dt_time(18, 0, 0, tzinfo=tz))

        candidates = [dt_util.as_utc(t) for t in (six_local, eighteen_local) if dt_util.as_utc(t) > now_utc]
        if candidates:
            return min(candidates)

        # ha mindkettő elmúlt, akkor holnap 06:00
        tomorrow = today + dt_timedelta(days=1)
        return dt_util.as_utc(dt_datetime.combine(tomorrow, dt_time(6, 0, 0, tzinfo=tz)))

    def _schedule_next() -> None:
        when = _next_boundary(dt_util.utcnow())
        if store.get("timer_unsub"):
            store["timer_unsub"]()
            store["timer_unsub"] = None
        store["timer_unsub"] = async_track_point_in_time(hass, _do_refresh, when)

    _schedule_next()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        rec = hass.data[DOMAIN].pop(entry.entry_id, {})
        if rec.get("timer_unsub"):
            rec["timer_unsub"]()
    return ok
