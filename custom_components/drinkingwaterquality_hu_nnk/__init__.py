from __future__ import annotations

from datetime import datetime as dt_datetime, time as dt_time, timedelta as dt_timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_point_in_time
from homeassistant.helpers.typing import ConfigType
from homeassistant.util import dt as dt_util
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, PLATFORMS
from .coordinator import NNKCoordinator

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    placemark_id = int(entry.data["placemark_id"])
    coord = NNKCoordinator(hass, placemark_id)
    await coord.async_config_entry_first_refresh()

    place = coord.data.place_name.strip() if coord.data else ""
    if place:
        hass.config_entries.async_update_entry(entry, title=place)

    try:
        reg = dr.async_get(hass)
        for dev in dr.async_entries_for_config_entry(reg, entry.entry_id):
            reg.async_update_device(
                dev.id,
                manufacturer="NNGYK",
                model="Ivóvíz minőség",
                name=f"Ivóvíz — {place or 'Település'}",
            )
    except Exception:
        pass


    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coord, "timer_unsub": None}

    store = hass.data[DOMAIN][entry.entry_id]

    async def _do_refresh(_now):
        await coord.async_request_refresh()
        _schedule_next()

    def _next_boundary(now_utc):
        local_now = dt_util.as_local(now_utc)
        today = local_now.date()
        tz = dt_util.get_time_zone(hass.config.time_zone)
        six_local = dt_datetime.combine(today, dt_time(6, 0, 0, tzinfo=tz))
        eighteen_local = dt_datetime.combine(today, dt_time(18, 0, 0, tzinfo=tz))
        cands = [dt_util.as_utc(t) for t in (six_local, eighteen_local) if dt_util.as_utc(t) > now_utc]
        if cands:
            return min(cands)
        tomorrow = today + dt_timedelta(days=1)
        return dt_util.as_utc(dt_datetime.combine(tomorrow, dt_time(6, 0, 0, tzinfo=tz)))

    def _schedule_next():
        when = _next_boundary(dt_util.utcnow())
        if store.get("timer_unsub"):
            store["timer_unsub"]()
            store["timer_unsub"] = None
        store["timer_unsub"] = async_track_point_in_time(hass, _do_refresh, when)

    _schedule_next()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        rec = hass.data[DOMAIN].pop(entry.entry_id, {})
        if rec.get("timer_unsub"):
            rec["timer_unsub"]()
    return ok
