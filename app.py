import folium
import shapely.wkb
import streamlit as st
from shapely import wkt
from streamlit_folium import st_folium

from data_processor import SpatialEngine
from routing import Router

if "engine" not in st.session_state:
    st.session_state.engine = SpatialEngine()

if "router" not in st.session_state:
    st.session_state.router = Router()

city = st.text_input("City", "Heidelberg")
amenity = st.selectbox("Find Near Me", ["hospital", "pharmacy", "cafe"])
travel_time = st.slider("Travel Time (mins)", 5, 30, 10)

if st.button("Analyze Reachability"):
    with st.spinner("Calculating..."):
        pois_gdf = st.session_state.engine.get_pois(city, amenity)
        first_geom = shapely.wkb.loads(pois_gdf.iloc[0].geometry)

        center_lat, center_lon = st.session_state.engine.get_city_geocode(city)

        iso_geojson = st.session_state.router.get_isochrone(
            center_lat, center_lon, travel_time
        )
        filtered_df = st.session_state.engine.filter_points_in_isochrone(iso_geojson)

        m = folium.Map(
            location=[center_lat, center_lon], zoom_start=13, tiles="cartodbpositron"
        )

        folium.Marker(
            location=[center_lat, center_lon],
            popup="City Location",
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(m)

        folium.GeoJson(
            iso_geojson,
            style_function=lambda x: {
                "fillColor": "#2ecc71",
                "color": "#27ae60",
                "fillOpacity": 0.3,
            },
        ).add_to(m)

        for _, row in filtered_df.iterrows():
            point = wkt.loads(row["wkt_geom"])
            folium.Marker(
                location=[point.y, point.x],
                popup=row["name"],
                icon=folium.Icon(color="blue", icon="info-sign"),
            ).add_to(m)

        st.title(f"{amenity.capitalize()} Accessibility")

        st_folium(
            m,
            use_container_width=True,
            returned_objects=[],
        )

        col1, col2 = st.columns(2)
        col1.metric("Total POIs Found", len(pois_gdf))
        col2.metric("POIs Within Reach", len(filtered_df))

        st.success(f"Found {len(filtered_df)} locations within {travel_time} mins.")
