import geopandas as gpd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import streamlit as st

# ------------------ LOAD DATA ------------------

@st.cache_data
def load_data():
    # baca shapefile asal (EPSG:27700 British National Grid)
    deaths = gpd.read_file("Cholera_Deaths.shp")
    pumps  = gpd.read_file("Pumps.shp")

    # convert ke WGS84 (lat/lon) untuk folium
    deaths_ll = deaths.to_crs(epsg=4326)
    pumps_ll  = pumps.to_crs(epsg=4326)

    return deaths_ll, pumps_ll

deaths_ll, pumps_ll = load_data()

# ------------------ SIDEBAR ------------------

st.sidebar.title("Controls")
show_deaths   = st.sidebar.checkbox("Show cholera deaths", value=True)
show_pumps    = st.sidebar.checkbox("Show water pumps", value=True)
show_heatmap  = st.sidebar.checkbox("Show deaths heatmap", value=False)

basemap = st.sidebar.selectbox(
    "Basemap style",
    ["CartoDB positron", "OpenStreetMap", "Stamen Toner", "Stamen Terrain"]
)

st.sidebar.markdown("---")
st.sidebar.write("Data: John Snow 1854 cholera outbreak")

# ------------------ TITLE & INTRO ------------------

st.title("John Snow 1854 Cholera Outbreak – Interactive Dashboard")

st.write(
    """
    This Streamlit dashboard recreates John Snow's classic cholera map in Soho, London (1854).

    Use the controls in the sidebar to toggle the cholera deaths, water pump layers,
    the basemap style, and an optional heatmap of deaths.
    """
)

with st.expander("About this map", expanded=False):
    st.markdown(
        """
        In 1854, Dr. John Snow mapped cholera deaths in Soho, London, and noticed
        that most cases clustered around the Broad Street water pump.
        By removing the pump handle, the outbreak was eventually contained.

        This dashboard reproduces that historical analysis using modern tools
        (GeoPandas, Folium, and Streamlit) to visualise how deaths are clustered
        in space relative to water pumps.
        """
    )

# ------------------ CREATE FOLIUM MAP ------------------

# pusat peta berdasarkan purata koordinat kematian
center = [
    deaths_ll.geometry.y.mean(),
    deaths_ll.geometry.x.mean()
]

m = folium.Map(location=center, zoom_start=17, tiles=basemap)

# layer deaths
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

# layer pumps
if show_pumps:
    fg_pumps = folium.FeatureGroup(name="Water pumps")
    for _, row in pumps_ll.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            icon=folium.Icon(color="blue", icon="tint"),
            popup="Water pump"
        ).add_to(fg_pumps)
    fg_pumps.add_to(m)

# optional heatmap
if show_heatmap:
    fg_heat = folium.FeatureGroup(name="Deaths heatmap")
    heat_data = [
        [row.geometry.y, row.geometry.x] for _, row in deaths_ll.iterrows()
    ]
    HeatMap(heat_data, radius=18, blur=15, min_opacity=0.3).add_to(fg_heat)
    fg_heat.add_to(m)

folium.LayerControl().add_to(m)

# paparkan map dalam streamlit
st_data = st_folium(m, width=800, height=550)

# ------------------ SIMPLE STATS ------------------

st.subheader("Basic statistics")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total cholera deaths", len(deaths_ll))
with col2:
    st.metric("Total water pumps", len(pumps_ll))

st.write("Sample of the deaths dataset:")
st.dataframe(deaths_ll.head())
