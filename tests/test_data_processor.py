import geopandas as gpd
from shapely.geometry import Point, Polygon
from src.data_processor import SpatialEngine

def test_init_creates_duckdb_connection():
    engine = SpatialEngine()
    assert engine.con is not None


def test_get_city_geocode_calls_osmnx_geocode(monkeypatch):
    called = {}

    def fake_geocode(city_name):
        called["city_name"] = city_name
        return (49.3988, 8.6724)

    monkeypatch.setattr("src.data_processor.ox.geocode", fake_geocode)

    engine = SpatialEngine()
    result = engine.get_city_geocode("Heidelberg")

    assert result == (49.3988, 8.6724)
    assert called["city_name"] == "Heidelberg"


def test_get_pois_filters_point_geometries(monkeypatch):
    point = Point(8.7, 49.4)
    polygon = Polygon([(8.66, 49.38), (8.68, 49.38), (8.68, 49.39), (8.66, 49.39)])
    gdf = gpd.GeoDataFrame(
        {"name": ["Point Place", "Polygon Area"], "geometry": [point, polygon]},
        geometry="geometry",
        crs="EPSG:4326",
    )

    def fake_features_from_place(city_name, tags):
        assert city_name == "Heidelberg"
        assert tags == {"amenity": "hospital"}
        return gdf

    monkeypatch.setattr("src.data_processor.ox.features_from_place", fake_features_from_place)

    engine = SpatialEngine()
    result = engine.get_pois("Heidelberg", amenity="hospital")

    assert len(result) == 1
    assert result.iloc[0]["name"] == "Point Place"
    assert isinstance(result.iloc[0]["geometry"], (bytes, bytearray))


def test_filter_points_in_isochrone_returns_only_points_inside():
    engine = SpatialEngine()

    gdf = gpd.GeoDataFrame(
        {"name": ["Inside", "Outside"], "geometry": [Point(0, 0), Point(10, 10)]},
        geometry="geometry",
        crs="EPSG:4326",
    )
    gdf["geometry"] = gdf["geometry"].to_wkb()
    engine.con.register("raw_pois", gdf)

    isochrone_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[-1.0, -1.0], [1.0, -1.0], [1.0, 1.0], [-1.0, 1.0], [-1.0, -1.0]]
                    ],
                },
                "properties": {},
            }
        ],
    }

    result = engine.filter_points_in_isochrone(isochrone_geojson)
    assert len(result) == 1
    assert result.iloc[0]["name"] == "Inside"
    assert "wkt_geom" in result.columns
    assert result.iloc[0]["wkt_geom"] == "POINT (0 0)"
