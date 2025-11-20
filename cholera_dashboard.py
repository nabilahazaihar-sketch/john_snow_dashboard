# cholera_dashboard.py

import geopandas as gpd
import folium
from streamlit_folium import st_folium
import streamlit as st

# ------------------ LOAD DATA ------------------

@st.cache_data
def load_data():
    # baca shapefile asal
    deaths = gpd.read_file("Cholera_Deaths.shp")
    pumps  = gpd.read_file("Pumps.shp")

    # convert ke lat/lon untuk folium
    deaths_ll = deaths.to_crs(epsg=4326)
    pumps_ll  = pumps.to_crs(epsg=4326)

    return deaths_ll, pumps_ll

deaths_ll, pumps_ll = load_data()

# ------------------ SIDEBAR ------------------

st.sidebar.title("Controls")
show_deaths = st.sidebar.checkbox("Show cholera deaths", value=True)
show_pumps  = st.sidebar.checkbox("Show water pumps", value=True)

st.sidebar.markdown("---")
st.sidebar.write("Data: John Snow 1854 cholera outbreak")

# ------------------ TITLE & DESCRIPTION ------------------

st.title("John Snow 1854 Cholera Outbreak – Interactive Dashboard")

st.write(
    """
    This Streamlit dashboard recreates John Snow's classic cholera map in Soho, London (1854).\n
    Use the checkboxes in the sidebar to toggle the cholera deaths and water pump layers.
    """
)

# ------------------ CREATE FOLIUM MAP ------------------

# pusat peta
center = [
    deaths_ll.geometry.y.mean(),
    deaths_ll.geometry.x.mean()
]

m = folium.Map(location=center, zoom_start=17, tiles="CartoDB positron")

# layer group supaya boleh on/off
if show_deaths:
    fg_deaths = folium.FeatureGroup(name="Cholera deaths")
    for _, row in deaths_ll.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=3,
            color="red",
            fill=True,
            fill_opacity=0.7
        ).add_to(fg_deaths)
    fg_deaths.add_to(m)

if show_pumps:
    fg_pumps = folium.FeatureGroup(name="Water pumps")
    for _, row in pumps_ll.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            icon=folium.Icon(color="blue", icon="tint"),
            popup="Water pump"
        ).add_to(fg_pumps)
    fg_pumps.add_to(m)

folium.LayerControl().add_to(m)

# paparkan map dalam streamlit
st_data = st_folium(m, width=700, height=500)

# ------------------ SIMPLE STATS ------------------

st.subheader("Basic statistics")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total cholera deaths", len(deaths_ll))
with col2:
    st.metric("Total water pumps", len(pumps_ll))

st.write("Sample of the deaths dataset:")
st.dataframe(deaths_ll.head())
