from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NNKCoordinator


class DWQProblemSensor(CoordinatorEntity[NNKCoordinator], BinarySensorEntity):
    """ON = probléma az ivóvíz minőségével."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: NNKCoordinator, name_base: str) -> None:
        super().__init__(coordinator)
        self._attr_name = f"Ivóvíz — {name_base}"
        self._attr_unique_id = f"dwq_problem_{coordinator._placemark_id}"

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def is_on(self) -> bool:
        d = self.coordinator.data
        return False if not d else (not d.ok)

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

    @property
    def device_info(self) -> dict[str, Any]:
        place = (self.coordinator.data.place_name if self.coordinator.data else "") or "Település"
        return {
            "identifiers": {(DOMAIN, f"placemark_{self.coordinator._placemark_id}")},
            "manufacturer": "NNGYK",
            "model": "Ivóvíz minőség",
            "name": f"Ivóvíz — {place}",
        }


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Platform-setup config entryből."""
    coord: NNKCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    name_base = (coord.data.place_name if coord.data else "") or entry.title or "Település"
    async_add_entities([DWQProblemSensor(coord, name_base)], update_before_add=True)
