from typing import Any, Dict, List, Optional

import openrouteservice as ors

from src.components.roadblock import RoadblockCache

BASE_URL = "http://localhost:8080/ors"


class Router:
    def __init__(self):

        self.ors_local_client = ors.Client(base_url=BASE_URL)
        self.ors_web_client = ors.Client(key="")

    def get_isochrone(self, lat, lon, time_limit=10):
        time_seconds = [time_limit * 60]

        body = {
            "locations": [[lon, lat]],  # ORS = [Longitude, Latitude]
            "range": time_seconds,
            "range_type": "time",
        }

        try:
            return self.ors_local_client.isochrones(**body)
        except Exception as e:
            raise RuntimeError(f"Isochrone request failed: {e}")

    def get_directions(
        self,
        start_coords: List[float],
        end_coords: List[float],
        avoid_polygons: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        roadblock_cache = RoadblockCache()

        body = {
            "coordinates": [
                roadblock_cache.normalize_coords(start_coords),
                roadblock_cache.normalize_coords(end_coords),
            ],
            "profile": "driving-car",
            "format": "geojson",
            "options": {},
        }

        if avoid_polygons:
            body["options"]["avoid_polygons"] = roadblock_cache.normalize_coords(
                avoid_polygons
            )

        try:
            return self.ors_local_client.directions(**body)
        except Exception as e:
            raise RuntimeError(f"Directions request failed: {e}")

    def get_elevation(self, coords: List[tuple[float, float]]):
        try:
            return self.ors_web_client.elevation_line(
                format_in="geojson",
                geometry={
                    "type": "LineString",
                    "coordinates": [
                        [49.415029, 8.692149],
                        [49.407036, 8.676892],
                    ],
                },
            )

        except Exception as e:
            raise RuntimeError(f"Directions request failed: {e}")
