"""Utilities for locating or downloading game cover images."""

import json
import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import quote
from urllib.request import Request, urlopen


class CoverFinder:
    """Find a local cover first, then use Steam's public store catalogue."""

    IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
    LOCAL_NAMES = ("cover", "poster", "boxart", "box_art", "header", "capsule")

    @classmethod
    def find_local_cover(cls, install_dir: str, title: str) -> str:
        """Return a likely image in the game folder, if one is available."""
        if not install_dir or not os.path.isdir(install_dir):
            return ""

        title_stem = cls._normalise(title)
        candidates = []
        for root, directories, files in os.walk(install_dir):
            relative_depth = len(Path(root).relative_to(install_dir).parts)
            if relative_depth >= 2:
                directories.clear()

            for filename in files:
                path = os.path.join(root, filename)
                stem, extension = os.path.splitext(filename)
                if extension.lower() not in cls.IMAGE_EXTENSIONS:
                    continue
                score = 0
                normalised_stem = cls._normalise(stem)
                if normalised_stem == title_stem:
                    score += 100
                if any(keyword in normalised_stem for keyword in cls.LOCAL_NAMES):
                    score += 50
                if score:
                    candidates.append((score, path))

        return max(candidates, default=(0, ""), key=lambda item: item[0])[1]

    @classmethod
    def download_steam_cover(cls, title: str, destination_dir: str = "assets/covers") -> str:
        """Download the closest matching Steam header image and return its local path."""
        app_id = cls._find_steam_app_id(title)
        if not app_id:
            return ""

        details_url = (
            "https://store.steampowered.com/api/appdetails?appids="
            f"{app_id}&l=english&cc=us"
        )
        details = cls._get_json(details_url)
        app_data = details.get(str(app_id), {}).get("data", {})
        image_url = app_data.get("header_image")
        if not image_url:
            return ""

        os.makedirs(destination_dir, exist_ok=True)
        safe_name = cls._normalise(app_data.get("name") or title) or str(app_id)
        destination = os.path.join(destination_dir, f"{safe_name}-{app_id}.jpg")
        request = Request(image_url, headers={"User-Agent": "LocalGameLibrary/0.1"})
        with urlopen(request, timeout=10) as response, open(destination, "wb") as image_file:
            image_file.write(response.read())
        return destination

    @classmethod
    def _find_steam_app_id(cls, title: str) -> Optional[int]:
        search_url = (
            "https://store.steampowered.com/api/storesearch/?term="
            f"{quote(title)}&l=english&cc=us"
        )
        items = cls._get_json(search_url).get("items", [])
        if not items:
            return None

        normalised_title = cls._normalise(title)
        exact_match = next(
            (item for item in items if cls._normalise(item.get("name", "")) == normalised_title),
            items[0],
        )
        return exact_match.get("id")

    @staticmethod
    def _get_json(url: str) -> dict:
        request = Request(url, headers={"User-Agent": "LocalGameLibrary/0.1"})
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def _normalise(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.lower())
