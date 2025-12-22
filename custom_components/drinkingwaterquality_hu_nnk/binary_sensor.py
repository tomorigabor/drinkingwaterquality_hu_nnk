from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NNKCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """
    Platform setup – HÁ-ból hívódik, amikor a config entry betöltődik.
    Nem csinál mást, mint előveszi a coordinator-t és felveszi az entitást.
    """
    coord: NNKCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([DrinkingWaterBinarySensor(entry, coord)], update_before_add=True)


class DrinkingWaterBinarySensor(CoordinatorEntity[NNKCoordinator], BinarySensorEntity):
    """Binary sensor for drinking water quality (NNGYK)."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_has_entity_name = True
    _attr_name = "Ivóvíz – Placemark"  # első pillanatban ez látszik; hamar felülírjuk
    _attr_icon = "mdi:cup-water"

    def __init__(self, entry: ConfigEntry, coordinator: NNKCoordinator) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"dwq_{entry.entry_id}"

    # ---- Állapot ----
    @property
    def is_on(self) -> bool:
        # PROBLÉMA device-class → on = probléma, off = rendben
        data = self.coordinator.data
        return False if (data and data.ok) else True

    # ---- Megjelenő név ----
    @property
    def name(self) -> str:
        place = (self.coordinator.data.place_name if self.coordinator.data else None) or "Település"
        return f"Ivóvíz — {place}"

    # ---- Device info (NE „Placemark”) ----
    @property
    def device_info(self) -> DeviceInfo:
        place = (self.coordinator.data.place_name if self.coordinator.data else None) or "Település"
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"Ivóvíz — {place}",
            manufacturer="NNGYK",
            model="Ivóvíz minőség",
            configuration_url=self.coordinator.source_url,
        )

    # ---- Attribútumok (magyar) ----
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        d = self.coordinator.data
        if not d:
            return {}
        return {
            "Település": d.place_name,
            "Minősítés": d.rating_text,
            "Forrás link": d.source_url,
            "Lekérdezési időpont": d.fetched_at,
        }
