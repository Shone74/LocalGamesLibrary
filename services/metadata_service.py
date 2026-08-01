"""Game metadata lookup independent from the user interface.

The service deliberately treats metadata as optional: callers can save and launch a
game before a lookup succeeds, then enrich it later when a connection is available.
"""

import json
import os
import re
import socket
from dataclasses import dataclass
from typing import Dict, Optional
from urllib.parse import quote
from urllib.request import Request, urlopen


@dataclass
class MetadataResult:
    """Metadata returned by a provider, with only safe-to-save local values."""

    title: str = ""
    genre: str = ""
    description: str = ""
    developer: str = ""
    publisher: str = ""
    release_date: str = ""
    cover_path: str = ""

    def to_dict(self) -> Dict[str, str]:
        return self.__dict__.copy()


class GameMetadataService:
    """Identify a game locally and enrich it through Steam when online."""

    COVER_DIRECTORY = "assets/covers"
    USER_AGENT = "LocalGameLibrary/0.2"

    @staticmethod
    def identify_executable(executable_path: str) -> Dict[str, str]:
        """Produce immediately available metadata without needing the network."""
        filename = os.path.splitext(os.path.basename(executable_path))[0]
        title = re.sub(r"[_-]+", " ", filename).strip()
        return {
            "title": title or "Unknown Game",
            "install_dir": os.path.dirname(executable_path),
        }

    @staticmethod
    def is_online() -> bool:
        """Use a short connection check so offline users are never held up."""
        try:
            with socket.create_connection(("store.steampowered.com", 443), timeout=2):
                return True
        except OSError:
            return False

    @classmethod
    def fetch_metadata(cls, title: str) -> Optional[MetadataResult]:
        """Fetch a Steam match and cache its cover locally; returns None on failure."""
        if not title or not cls.is_online():
            return None

        try:
            app_id = cls._find_steam_app_id(title)
            if not app_id:
                return None
            details = cls._get_json(
                "https://store.steampowered.com/api/appdetails?appids="
                f"{app_id}&l=english&cc=us"
            )
            data = details.get(str(app_id), {}).get("data", {})
            if not data:
                return None
            genres = ", ".join(item.get("description", "") for item in data.get("genres", []))
            result = MetadataResult(
                title=data.get("name", ""),
                genre=genres,
                description=data.get("short_description", ""),
                developer=", ".join(data.get("developers", [])),
                publisher=", ".join(data.get("publishers", [])),
                release_date=data.get("release_date", {}).get("date", ""),
            )
            image_url = data.get("header_image", "")
            if image_url:
                result.cover_path = cls._download_cover(image_url, result.title or title, app_id)
            return result
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            return None

    @classmethod
    def _find_steam_app_id(cls, title: str) -> Optional[int]:
        data = cls._get_json(
            "https://store.steampowered.com/api/storesearch/?term="
            f"{quote(title)}&l=english&cc=us"
        )
        items = data.get("items", [])
        if not items:
            return None
        normalised_title = cls._normalise(title)
        match = next(
            (item for item in items if cls._normalise(item.get("name", "")) == normalised_title),
            items[0],
        )
        return match.get("id")

    @classmethod
    def _download_cover(cls, image_url: str, title: str, app_id: int) -> str:
        os.makedirs(cls.COVER_DIRECTORY, exist_ok=True)
        safe_name = cls._normalise(title) or str(app_id)
        destination = os.path.join(cls.COVER_DIRECTORY, f"{safe_name}-{app_id}.jpg")
        if os.path.exists(destination):
            return destination
        request = Request(image_url, headers={"User-Agent": cls.USER_AGENT})
        with urlopen(request, timeout=10) as response, open(destination, "wb") as image_file:
            image_file.write(response.read())
        return destination

    @classmethod
    def _get_json(cls, url: str) -> dict:
        request = Request(url, headers={"User-Agent": cls.USER_AGENT})
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def _normalise(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.lower())
