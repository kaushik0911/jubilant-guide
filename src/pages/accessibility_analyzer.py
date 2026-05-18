import folium
import streamlit as st
from shapely import wkt
from streamlit_folium import st_folium

from src.components.isochrone import IsochroneFilter
from src.routing import Router

router = Router()


def main():
    st.set_page_config(
        page_title="Accessibility Analyzer",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Accessibility Analyzer")
    st.markdown(
        "Discover Points of Interest (POIs) accessible within a travel time range from a city location."
    )

    st.header("Configuration")
    city = st.text_input("City", "Heidelberg", help="Enter a city name")
    amenity = st.selectbox(
        "Find Near Me",
        ["hospital", "pharmacy", "cafe", "restaurant", "bank", "school"],
        help="Select the type of amenity to search for",
    )
    travel_time = st.slider(
        "Travel Time (mins)",
        5,
        30,
        10,
        help="Maximum travel time to search within",
    )

    if st.button("Analyze Reachability", type="primary", use_container_width=True):
        with st.spinner("Calculating..."):
            try:

                pois_gdf = IsochroneFilter().get_pois(city, amenity)

                if pois_gdf.empty:
                    st.warning(f"No {amenity} found in {city}")
                    return

                city_center_lat, city_center_lon = IsochroneFilter().get_city_geocode(
                    city
                )

                isochrones_geojson = router.get_isochrone(
                    city_center_lat, city_center_lon, travel_time
                )

                accessible_pois = IsochroneFilter().filter_points_in_isochrone(
                    pois_gdf, isochrones_geojson
                )

                m = folium.Map(
                    location=[city_center_lat, city_center_lon],
                    zoom_start=13,
                    tiles="cartodbpositron",
                )

                folium.Marker(
                    location=[city_center_lat, city_center_lon],
                    popup="City Location",
                    icon=folium.Icon(color="red", icon="info-sign"),
                ).add_to(m)

                folium.GeoJson(
                    isochrones_geojson,
                    style_function=lambda x: {
                        "fillColor": "#2ecc71",
                        "color": "#27ae60",
                        "fillOpacity": 0.3,
                    },
                    name="Reachable Area",
                ).add_to(m)

                for _, row in accessible_pois.iterrows():
                    point = wkt.loads(row["wkt_geom"])
                    folium.Marker(
                        location=[point.y, point.x],  # type: ignore
                        popup=row["name"],
                        tooltip=row["name"],
                        icon=folium.Icon(color="blue", icon="info-sign"),
                    ).add_to(m)

                folium.LayerControl().add_to(m)

                st.title(f"{amenity.capitalize()} Accessibility in {city}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total POIs Found", len(pois_gdf))
                with col2:
                    st.metric("POIs Within Reach", len(accessible_pois))
                with col3:
                    percentage = (
                        (len(accessible_pois) / len(pois_gdf) * 100)
                        if len(pois_gdf) > 0
                        else 0
                    )
                    st.metric("Coverage", f"{percentage:.1f}%")

                st_folium(
                    m,
                    width=True,
                    height=600,
                    returned_objects=[],
                )

                st.success(
                    f"Found {len(accessible_pois)} {amenity} locations within {travel_time} mins from {city}."
                )

                with st.expander("View all accessible POIs"):
                    st.dataframe(
                        accessible_pois,
                        width=True,
                        hide_index=True,
                    )

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Make sure the ORS service is running on localhost:8080")


if __name__ == "__main__":
    main()
