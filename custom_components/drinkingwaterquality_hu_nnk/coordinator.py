from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import URL_TEMPLATE, OK_PHRASES

_LOGGER = logging.getLogger(__name__)

def _norm(s: str) -> str:
    return " ".join((s or "").strip().split()).lower()

@dataclass
class DWQData:
    ok: bool
    place_name: str
    rating_text: str
    source_url: str
    fetched_at: str

class NNKCoordinator(DataUpdateCoordinator[DWQData]):
    def __init__(self, hass: HomeAssistant, placemark_id: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="NNGYK Drinking Water",
            update_method=self._async_update_data,
        )
        self._placemark_id = placemark_id
        self.source_url = URL_TEMPLATE.format(placemark_id=placemark_id)

    async def _fetch_html(self, url: str) -> str:
        session: ClientSession = async_get_clientsession(self.hass)
        async with session.get(url, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def _async_update_data(self) -> DWQData:
        html = await self._fetch_html(self.source_url)
        soup = BeautifulSoup(html, "html.parser")

        rating = _extract_rating(soup) or ""
        place = _extract_place(soup) or ""

        ok = any(_norm(rating) == _norm(p) for p in OK_PHRASES)
        fetched = dt_util.now().strftime("%Y-%m-%d %H:%M:%S")

        return DWQData(
            ok=ok,
            place_name=place or "Ismeretlen település",
            rating_text=rating or "Ismeretlen minősítés",
            source_url=self.source_url,
            fetched_at=fetched,
        )

def _extract_place(soup: BeautifulSoup) -> Optional[str]:
    for el in soup.find_all(["strong","b","span","th","td","p","div"]):
        text = " ".join(el.get_text(separator=" ", strip=True).split())
        m = re.search(r"Település(?: neve)?\s*:\s*(.+)", text, flags=re.I)
        if m:
            candidate = m.group(1).strip()
            candidate = re.split(r"\s+Minősítés\s*:", candidate)[0].strip()
            return candidate

    for tr in soup.find_all("tr"):
        cells = tr.find_all(["th","td"])
        for i, c in enumerate(cells):
            label = " ".join(c.get_text(" ", strip=True).split()).lower()
            if label in ("település", "település neve"):
                if i+1 < len(cells):
                    return " ".join(cells[i+1].get_text(" ", strip=True).split())
    for tag in soup.find_all(["h1","h2","title"]):
        t = " ".join(tag.get_text(" ", strip=True).split())
        if "ivóvíz" in t.lower() and "–" in t:
            return t.split("–",1)[0].strip()
    return None

def _extract_rating(soup: BeautifulSoup) -> Optional[str]:
    for el in soup.find_all(["strong","b","span","th","td","p","div"]):
        text = " ".join(el.get_text(separator=" ", strip=True).split())
        m = re.search(r"Minősítés\s*:\s*(.+)", text, flags=re.I)
        if m:
            rating = m.group(1).strip()
            rating = rating.split("  ")[0].strip()
            rating = re.split(r"\s+Paraméter neve|\s+Ivóvízben|\s+Visszautalás|\s+Megjegyzés", rating)[0].strip()
            return rating

    for tr in soup.find_all("tr"):
        cells = tr.find_all(["th","td"])
        for i, c in enumerate(cells):
            if "minősítés" in " ".join(c.get_text(" ", strip=True).split()).lower():
                if i+1 < len(cells):
                    return " ".join(cells[i+1].get_text(" ", strip=True).split())
    return None
