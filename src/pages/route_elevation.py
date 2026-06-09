import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from src.components.elevation import ElevationCache
from src.routing import Router

cache = ElevationCache()
router = Router()

EXISTING_ROUTE = [
    [49.408663957747, 8.689759402170136],
    [49.41017207323517, 8.686369285199621],
]


def main() -> None:
    st.set_page_config(page_title="Path Elevation Extractor", layout="wide")
    st.title("Path Elevation Extractor")

    results = [None] * len(EXISTING_ROUTE)
    missing_indices = []
    missing_query_coords = []

    for idx, pt in enumerate(EXISTING_ROUTE):
        lat, lon = pt[0], pt[1]

        cache_key = f"{lon:.6f}_{lat:.6f}"
        cached_elevation = cache.get(cache_key)
        if cached_elevation is not None:
            print("found", cache_key)
            results[idx] = {
                "longitude": lon,
                "latitude": lat,
                "elevation": cached_elevation,
                "source": "Disk Cache",
            }
        else:
            missing_indices.append(idx)
            missing_query_coords.append([lon, lat])

    if missing_query_coords:
        elevations = router.get_elevation(missing_query_coords)
        three_d_coords = elevations["geometry"]["coordinates"]

        for elevation_idx, result_pt in enumerate(three_d_coords):
            elevation = result_pt[2]
            original_index = missing_indices[elevation_idx]
            lat, lon = EXISTING_ROUTE[original_index]

            results[original_index] = {
                "longitude": lon,
                "latitude": lat,
                "elevation": elevation,
                "source": "ORS Service",
            }

            cache_key = f"{lon:.6f}_{lat:.6f}"
            cache.set(cache_key, elevation)

    df = pd.DataFrame(results)
    df["point_index"] = df.index

    st.write("### Data Source Log")
    st.dataframe(df[["point_index", "latitude", "longitude", "elevation", "source"]])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Chart Profile")
        fig = px.line(df, x="point_index", y="elevation", template="plotly_dark")
        fig.update_traces(line_color="#2ecc71", line_width=3)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("OpenStreetMap Route View")
        map_center = [df["latitude"].mean(), df["longitude"].mean()]
        m = folium.Map(location=map_center, zoom_start=14)

        folium_line = list(zip(df["latitude"], df["longitude"]))
        folium.PolyLine(folium_line, color="#2ecc71", weight=6).add_to(m)

        for _, row in df.iterrows():
            marker_color = "green" if row["source"] == "Disk Cache" else "blue"
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=6,
                color=marker_color,
                fill=True,
                popup=f"{row['source']} ({row['elevation']}m)",
            ).add_to(m)

        st_folium(m, use_container_width=True, height=400)


if __name__ == "__main__":
    main()
