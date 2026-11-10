"""
TFB3133/TEB3133 Data Visualization - Lab 7
Interactive Map Visualization Examples using Streamlit

Run with:  streamlit run lab7_maps.py
(needs the folder ne_110m_admin_0_countries/ next to this file)
"""
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


# Load the Natural Earth dataset.
# Adds a 'pop_est' column with random estimates if it is not present.
@st.cache_data
def load_data():
    gdf = gpd.read_file("ne_110m_admin_0_countries.shp")
    if "pop_est" not in gdf.columns:
        if "POP_EST" in gdf.columns:      # Natural Earth stores real estimates here
            gdf["pop_est"] = gdf["POP_EST"]
        else:
            np.random.seed(0)
            gdf["pop_est"] = np.random.randint(1e6, 1e9, size=len(gdf))
    return gdf


gdf = load_data()

# Projections used in the "Geo Projection" example (the lab uses this
# dictionary without defining it, so it is defined here).
projection_options = {
    "WGS84 (Plate Carrée)": "EPSG:4326",
    "Web Mercator": "EPSG:3857",
    "Robinson": "ESRI:54030",
    "Mollweide (equal area)": "ESRI:54009",
    "Equal Earth": "EPSG:8857",
}


def add_pop_density(frame, use_log):
    """Population per square km, using areas computed in an equal-area CRS
    (areas in degrees, as in the lab text, are distorted)."""
    area_km2 = frame.to_crs("EPSG:6933").geometry.area / 1e6
    density = frame["pop_est"] / area_km2
    return np.log1p(density) if use_log else density


st.title("Interactive Map Visualization Examples")
st.sidebar.header("Choose a Map Type")
map_type = st.sidebar.radio("Select Map Type", [
    "Map Cosmetics",
    "Map Visual Hierarchy",
    "Choropleth Map",
    "Geo Projection",
])

# 1. Map Cosmetics ---------------------------------------------------------------
if map_type == "Map Cosmetics":
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(ax=ax, color="skyblue", edgecolor="black", linewidth=0.5)
    ax.set_title("Styled Map Example", fontsize=15, fontweight="bold")
    ax.set_facecolor("lightgrey")
    st.pyplot(fig)

# 2. Map Visual Hierarchy --------------------------------------------------------
elif map_type == "Map Visual Hierarchy":
    country_col = "name" if "name" in gdf.columns else "NAME"
    highlighted_countries = st.multiselect(
        "Select countries to highlight in red",
        sorted(gdf[country_col].unique()),
        default=["Brazil", "India", "China", "Australia", "South Africa", "Russia"],
    )
    gdf["color"] = gdf[country_col].apply(
        lambda x: "red" if x in highlighted_countries else "skyblue")
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(color=gdf["color"], edgecolor="black", linewidth=0.5, ax=ax)
    ax.set_title("Map Visual Hierarchy with Selected Countries Highlighted in Red")
    st.pyplot(fig)

# 3. Choropleth Map ---------------------------------------------------------------
elif map_type == "Choropleth Map":
    color_choice = st.selectbox(
        "Choose Color Scheme", ["OrRd", "YlGn", "Blues", "Purples", "Greens"], index=0)
    use_log_scale = st.checkbox("Use Log Transformation", value=True)
    gdf["pop_density"] = add_pop_density(gdf, use_log_scale)
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf.plot(column="pop_density", cmap=color_choice, edgecolor="black",
             legend=True, ax=ax)
    ax.set_title(f"Population Density by Country (Color Scheme: {color_choice})")
    st.pyplot(fig)
    st.caption("Density = population per km². The log transformation stops a few "
               "very dense countries from making all the others look the same.")

# 4. Geo Projection ---------------------------------------------------------------
elif map_type == "Geo Projection":
    proj_choice = st.selectbox("Select a Projection", list(projection_options.keys()))
    color_choice = st.selectbox(
        "Choose Color Scheme", ["OrRd", "YlGn", "Blues", "Purples", "Greens"], index=0)
    use_log_scale = st.checkbox("Use Log Transformation for Population Density",
                                value=True)
    gdf["pop_density"] = add_pop_density(gdf, use_log_scale)
    gdf_proj = gdf.to_crs(projection_options[proj_choice])
    fig, ax = plt.subplots(figsize=(10, 6))
    gdf_proj.plot(column="pop_density", cmap=color_choice, edgecolor="black",
                  legend=True, ax=ax)
    ax.set_title(f"Map in {proj_choice} Projection")
    st.pyplot(fig)
    st.caption("The same data looks different in each projection: Mercator "
               "inflates areas near the poles, equal-area projections "
               "(Mollweide, Equal Earth) keep sizes comparable.")
