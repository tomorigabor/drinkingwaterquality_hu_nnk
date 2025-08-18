from __future__ import annotations

import re
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NNKCoordinator

def _slug(s: str) -> str:
    import unicodedata
    s_norm = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[^a-zA-Z0-9]+", "_", s_norm).strip("_").lower()

class DrinkingWaterBinary(CoordinatorEntity[NNKCoordinator], BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: NNKCoordinator, object_id: str, display_place: str, placemark_id: int) -> None:
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._display_place = display_place
        self._placemark_id = placemark_id
        self._attr_unique_id = object_id
        self._attr_name = f"Ivóvíz — {display_place}"

    @property
    def is_on(self) -> bool:
        return not self.coordinator.data.ok

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"id:{self._placemark_id}"), (DOMAIN, f"place:{self._display_place}")},
            manufacturer="NNGYK",
            model="Ivóvíz minőség",
            name=f"Ivóvíz — {self._display_place}",
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data
        return {
            "Település": d.place_name,
            "Minősítés": d.rating_text,
            "Forrás link": d.source_url,
            "Lekérdezési időpont": d.fetched_at,
        }

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coord: NNKCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    place = coord.data.place_name
    object_id = f"ivoviz_{_slug(place)}"
    async_add_entities([DrinkingWaterBinary(coord, object_id, place, int(entry.data["placemark_id"]))])
