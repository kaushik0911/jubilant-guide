from typing import Any, Dict, List, Optional

from openrouteservice import client

from src.helpers.roadblock import RoadblockCache

BASE_URL = "http://localhost:8080/ors"


class Router:
    def __init__(self):

        self.ors_client = client.Client(base_url=BASE_URL)

    def get_isochrone(self, lat, lon, time_limit=10):
        time_seconds = [time_limit * 60]

        body = {
            "locations": [[lon, lat]],  # ORS = [Longitude, Latitude]
            "range": time_seconds,
            "range_type": "time",
        }

        try:
            return self.ors_client.isochrones(**body)
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
            route = self.ors_client.directions(**body)

            return route
        except Exception as e:
            raise RuntimeError(f"Directions request failed: {e}")
