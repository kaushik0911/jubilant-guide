import osmnx as ox

from src.db import DBConnector


class IsochroneFilter:

    @staticmethod
    def get_city_geocode(city_name):
        return ox.geocode(city_name)

    @staticmethod
    def get_pois(city_name, amenity="hospital"):

        gdf = ox.features_from_place(city_name, tags={"amenity": amenity})

        gdf = gdf.reset_index()
        gdf = gdf[gdf.geom_type == "Point"][["name", "geometry"]].copy()
        gdf["geometry"] = gdf["geometry"].to_wkb()

        return gdf

    @staticmethod
    def filter_points_in_isochrone(gdf, isochrone_geojson):
        import json

        db_connector = DBConnector()
        db_connector.connection.register("gdf", gdf)

        iso_json_str = json.dumps(isochrone_geojson["features"][0]["geometry"])

        query = """
            SELECT name, ST_AsText(ST_GeomFromWKB(geometry)) as wkt_geom
            FROM gdf
            WHERE ST_Intersects(
                ST_GeomFromWKB(geometry),
                ST_GeomFromGeoJSON(?)
            )
        """

        filtered_points = db_connector.connection.execute(
            query, [iso_json_str]
        ).fetchdf()

        db_connector.disconnect()

        return filtered_points
