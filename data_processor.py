import duckdb
import osmnx as ox


class SpatialEngine:
    def __init__(self):
        self.con = duckdb.connect(database=":memory:")
        self.con.execute("INSTALL spatial; LOAD spatial;")

    def get_city_geocode(self, city_name):
        return ox.geocode(city_name)

    def get_pois(self, city_name, amenity="hospital"):

        gdf = ox.features_from_place(city_name, tags={"amenity": amenity})

        gdf = gdf.reset_index()
        gdf = gdf[gdf.geom_type == "Point"][["name", "geometry"]].copy()
        gdf["geometry"] = gdf["geometry"].to_wkb()

        self.con.register("raw_pois", gdf)

        return gdf

    def filter_points_in_isochrone(self, isochrone_geojson):
        import json

        iso_json_str = json.dumps(isochrone_geojson["features"][0]["geometry"])

        query = """
            SELECT name, ST_AsText(ST_GeomFromWKB(geometry)) as wkt_geom
            FROM raw_pois
            WHERE ST_Intersects(
                ST_GeomFromWKB(geometry),
                ST_GeomFromGeoJSON(?)
            )
        """

        return self.con.execute(query, [iso_json_str]).fetchdf()
