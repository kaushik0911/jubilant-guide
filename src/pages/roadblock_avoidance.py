import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from src.helpers.roadblock import (
    RoadblockCache,
    RoadblockFilter,
    RoadblockVisualizer,
)
from src.routing import Router

cache = RoadblockCache()
router = Router()


def main() -> None:
    st.set_page_config(page_title="Roadblock Avoidance", layout="wide")

    st.title("Route Planning with Roadblock Avoidance")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Start Point")
        start_lat = st.number_input(
            "Start Latitude", format="%.6f", key="start_lat", value=49.41502858424546
        )
        start_lon = st.number_input(
            "Start Longitude", format="%.6f", key="start_lon", value=8.692149025906376
        )

    with col2:
        st.write("End Point")
        end_lat = st.number_input(
            "End Latitude", format="%.6f", key="end_lat", value=49.40703603905464
        )
        end_lon = st.number_input(
            "End Longitude", format="%.6f", key="end_lon", value=8.67689213071828
        )

    start = [start_lon, start_lat]
    end = [end_lon, end_lat]

    if not all([start, end]):
        st.warning("Please enter start and end coordinates")
        return

    uploaded_file = st.file_uploader(
        "Upload Roadblocks CSV",
        type="csv",
        help="CSV file with columns: latitude, longitude",
    )

    roadblocks = []
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            for idx, row in df.iterrows():
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                roadblocks.append((lat, lon))

        except Exception as e:
            st.error(f"Error reading CSV: {str(e)}")

    if st.button("Calculate Route", type="primary"):

        with st.spinner("Calculating optimal route..."):
            try:
                cache_key = cache.generate_cache_key(start, end, roadblocks)
                cached_route = cache.get(cache_key)

                if cached_route:
                    route = cached_route
                else:
                    relevant_blockers = RoadblockFilter.get_relevant_blockers(
                        start, end, roadblocks
                    )

                    if relevant_blockers:
                        relevant_blockers.sort()
                        avoid_polygons = RoadblockFilter.convert_blockers_to_polygons(
                            relevant_blockers
                        )
                    else:
                        avoid_polygons = None

                    route = router.get_directions(start, end, avoid_polygons)

                cache.set(cache_key, route)

                folium_map = RoadblockVisualizer.create_route_map(
                    (start[1], start[0]),
                    (end[1], end[0]),
                    route,
                    roadblocks=roadblocks,
                    start_label="Start",
                    end_label="End",
                )

                st_folium(
                    folium_map,
                    width=True,
                    height=600,
                    returned_objects=[],
                )

            except Exception as e:
                st.error(f"Error calculating route: {str(e)}")
                st.write("Make sure the ORS service is running on localhost:8080")


if __name__ == "__main__":
    main()
