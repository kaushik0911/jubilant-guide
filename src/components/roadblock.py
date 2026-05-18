import hashlib
import json
from typing import List, Tuple

import folium
from shapely.geometry import Point

from src.cache import AppCache


class RoadblockCache(AppCache):
    def __init__(self):
        super().__init__()

    def normalize_coords(self, obj, precision: int = 5):
        if isinstance(obj, float):
            return round(obj, precision)
        if isinstance(obj, dict):
            return {k: self.normalize_coords(v, precision) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self.normalize_coords(x, precision) for x in obj]
        return obj

    def generate_cache_key(
        self, start: List[float], end: List[float], roadblocks: List[Tuple]
    ) -> str:
        key_data = {
            "start": self.normalize_coords(start),
            "end": self.normalize_coords(end),
            "blocks": self.normalize_coords(sorted(roadblocks)),
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()


class RoadblockFilter:
    @staticmethod
    def get_relevant_blockers(
        start: List[float],
        end: List[float],
        all_blockers: List[Tuple],
        buffer_degrees: float = 0.05,
    ) -> List[Tuple]:

        min_lon = min(start[0], end[0]) - buffer_degrees
        max_lon = max(start[0], end[0]) + buffer_degrees
        min_lat = min(start[1], end[1]) - buffer_degrees
        max_lat = max(start[1], end[1]) + buffer_degrees

        return [
            (lat, lon)
            for lat, lon in all_blockers
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
        ]

    @staticmethod
    def convert_blockers_to_polygons(
        blockers: List[Tuple], buffer_size: float = 0.0003
    ):
        return {
            "type": "MultiPolygon",
            "coordinates": [
                [list(Point(lon, lat).buffer(buffer_size).exterior.coords)]
                for lat, lon in blockers
            ],
        }


class RoadblockVisualizer:
    @staticmethod
    def create_base_map(
        center_lat: float, center_lon: float, zoom: int = 15
    ) -> folium.Map:
        return folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom,
            tiles="cartodbpositron",
        )

    @staticmethod
    def get_route(m: folium.Map, route_geojson) -> folium.Map:
        folium.GeoJson(
            route_geojson,
            name="Route",
            style_function=lambda x: {
                "color": "green",
                "weight": 5,
                "opacity": 0.8,
            },
        ).add_to(m)

        return m

    @staticmethod
    def add_marker(
        m: folium.Map,
        lat: float,
        lon: float,
        label: str,
        icon_color: str = "blue",
        popup: str = "",
    ) -> folium.Map:
        folium.Marker(
            location=[lat, lon],
            popup=popup or label,
            tooltip=label,
            icon=folium.Icon(color=icon_color, icon="info-sign"),
        ).add_to(m)
        return m

    @staticmethod
    def add_roadblocks_to_map(
        m: folium.Map, blockers: List[Tuple], radius: int = 20, color: str = "red"
    ) -> folium.Map:
        for lat, lon in blockers:
            folium.Circle(
                location=[lat, lon],
                radius=radius,
                color=color,
                fill=True,
                fillOpacity=0.7,
                popup="Roadblock",
            ).add_to(m)
        return m

    @staticmethod
    def create_route_map(
        start: Tuple[float, float],
        end: Tuple[float, float],
        route_geojson,
        roadblocks: List[Tuple] = [
            (),
        ],
        start_label: str = "Start",
        end_label: str = "End",
    ) -> folium.Map:
        center_lat = (start[0] + end[0]) / 2
        center_lon = (start[1] + end[1]) / 2

        m = RoadblockVisualizer.create_base_map(center_lat, center_lon)
        m = RoadblockVisualizer.add_marker(m, start[0], start[1], start_label, "blue")
        m = RoadblockVisualizer.add_marker(m, end[0], end[1], end_label, "red")

        if roadblocks:
            m = RoadblockVisualizer.add_roadblocks_to_map(m, roadblocks)

        m = RoadblockVisualizer.get_route(m, route_geojson)

        return m
