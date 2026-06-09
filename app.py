import streamlit as st


def main() -> None:
    st.set_page_config(layout="wide")

    pages = [
        st.Page(
            "./src/pages/accessibility_analyzer.py", title="Accessibility Analyzer"
        ),
        st.Page("./src/pages/roadblock_avoidance.py", title="Roadblock Avoidance"),
        st.Page("./src/pages/route_elevation.py", title="Path Elevation Extractor"),
    ]

    pg = st.navigation(pages, position="top")
    pg.run()


if __name__ == "__main__":
    main()
