import base64
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import streamlit as st
from functions import *

# ================== CONFIG ==================
st.set_page_config(
    page_title="The Data Project - Plataforma",
    page_icon="./static/logos/TDP-circle-white.svg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ================== PATHS ===================
logo_path = "./static/logos/TDP_Logo_White.svg"
shp_path = "./data/PAN_adm2.shp"
tif_path = "./data/dem-cr.tiff"

# ================== ESTADO ==================
if "selected_module" not in st.session_state:
    st.session_state["selected_module"] = None

# Definimos la “config” de los 6 módulos en un solo sitio
MODULES = [
    {
        "key": "demo",
        "title": "Demografía y Territorio",
        "logo": "./static/logos/demografia.png",
        "dashboards": [
            "Censo poblacional",
            "Tendencias demográficas",
            "Migración interna",
            "Uso del suelo",
        ],
    },
    {
        "key": "eco",
        "title": "Economía y Empleo",
        "logo": "./static/logos/economia.png",
        "dashboards": [
            "PIB regional",
            "Tasa de empleo",
            "Sectores económicos",
            "Comercio local",
        ],
    },
    {
        "key": "salud_seg",
        "title": "Salud y Seguridad",
        "logo": "./static/logos/salud-seguridad.png",
        "dashboards": [
            "Incidencia de enfermedades",
            "Mapa de riesgo epidemiológico",
            "Delitos reportados",
        ],
    },
    {
        "key": "infra",
        "title": "Infraestructura y Servicios",
        "logo": "./static/logos/infraestructuras.png",
        "dashboards": [
            "Agua potable",
            "Acceso a electricidad",
            "Infraestructura energética",
            "Energías renovables",
        ],
    },
    {
        "key": "medioamb",
        "title": "Medioambiente y Clima",
        "logo": "./static/logos/medioambiente.png",
        "dashboards": [
            "Calidad del aire",
            "Cobertura forestal",
            "Zonas vulnerables",
            "Cambio climático",
        ],
    },
    {
        "key": "opinion",
        "title": "Opinión pública",
        "logo": "./static/logos/opinion.png",
        "dashboards": [
            "Encuesta nacional",
            "Encuesta de calidad de vida",
            "Encuesta de percepción de seguridad",
            "Encuesta de percepción del gobierno",
        ],
    },
]

# Diccionario con la información de cada dashboard
DASHBOARD_INFO = {
    "Censo poblacional": "Información detallada sobre la distribución de la población, por región, edad y género.",
    "Tendencias demográficas": "Análisis de las tendencias poblacionales, incluyendo crecimiento y migración.",
    "Migración interna": "Estudio sobre los flujos migratorios dentro del país.",
    "Uso del suelo": "Datos sobre cómo se distribuye el uso del suelo en el territorio.",
    "PIB regional": "Información sobre el Producto Interno Bruto a nivel regional.",
    "Tasa de empleo": "Estudio sobre las tasas de empleo en diferentes sectores económicos.",
    "Sectores económicos": "Análisis de los sectores económicos más relevantes del país.",
    "Comercio local": "Información sobre el comercio a nivel local y su impacto económico.",
    "Incidencia de enfermedades": "Estudio de la incidencia de enfermedades en diferentes regiones.",
    "Mapa de riesgo epidemiológico": "Mapa que muestra los niveles de riesgo de enfermedades.",
    "Delitos reportados": "Estadísticas sobre la incidencia de delitos en el país.",
    "Agua potable": "Análisis de acceso y cobertura de agua potable.",
    "Acceso a electricidad": "Estudio sobre el acceso a la electricidad en diversas zonas.",
    "Infraestructura energética": "Datos sobre la infraestructura energética del país.",
    "Energías renovables": "Información sobre el uso y expansión de las energías renovables.",
    "Calidad del aire": "Indicadores sobre la calidad del aire en distintas regiones.",
    "Cobertura forestal": "Análisis sobre la cobertura y pérdida de bosques.",
    "Zonas vulnerables": "Estudio sobre las zonas vulnerables a desastres naturales.",
    "Cambio climático": "Impactos del cambio climático en el país.",
    "Encuesta nacional": "Encuesta sobre la percepción y actitudes de la población.",
    "Encuesta de calidad de vida": "Estudio sobre la calidad de vida de los ciudadanos.",
    "Encuesta de percepción de seguridad": "Encuesta sobre cómo la población percibe la seguridad en su comunidad.",
    "Encuesta de percepción del gobierno": "Estudio sobre la percepción pública del gobierno."
}


#  ================== ESTILOS ===================
st.markdown(
    """
<style>
@font-face {
  font-family: 'PoppinsLocal';
  src: url('./static/Poppins-Regular.woff2') format('woff2'),
       url('./static/Poppins-Regular.ttf') format('truetype');
  font-weight: 300;
  font-style: normal;
  font-display: swap;
}

[data-testid="stAppViewContainer"] {
  background: linear-gradient(90deg, #175CA1, #07A9E0 140%);
  background-attachment: fixed;
}

.header-row { display:flex; align-items:center; gap:12px; }
.header-row h1 { margin:0; font-size:4vh; font-weight:500; color:#fff; }
.header-row img { height:5vh; width:auto; }

.block-container label:empty { margin:0; padding:0; }
footer { visibility: hidden; }
section[data-testid="stSidebar"] { display:none !important; }
header[data-testid="stHeader"] { display:none !important; }
MainMenu { visibility: hidden; }
main blockquote, .block-container { padding-top: 0.6rem; padding-bottom: 0.6rem; }

</style>
""",
    unsafe_allow_html=True,
)

# ================== DATA (Aqui va la carga y procesado de datos) ==================
logo_data_uri = img_to_data_uri(logo_path)

# ================== CABECERA ==================
st.markdown(
    f"""
    <div class="header-box">
      <div class="header-row">
        <img src="{logo_data_uri}" alt="TDP Logo" />
        <h1>Plataforma</h1>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ================== TABLERO ==================
columna1, columna2 = st.columns([2, 1.2])

# --------- COLUMNA IZQUIERDA: MÓDULOS + “VENTANA” DE DASHBOARDS ---------
with columna1:
    # Grid 3x2 de módulos
    row1 = MODULES[:3]
    row2 = MODULES[3:]

    for row in (row1, row2):
        cols = st.columns(len(row))
        for col, module in zip(cols, row):
            with col:
                with st.container(border=True, height=270):
                    # columnas internas solo para centrar
                    left, center, right = st.columns([0.7, 2, 0.7])
                    with center:
                        logo_uri = img_to_data_uri(module["logo"])
                        st.image(logo_uri, use_container_width=True, width=100)

                        clicked = st.button(
                            module["title"],
                            key=f"btn_{module['key']}", use_container_width=True
                        )
                        if clicked:
                            st.session_state["selected_module"] = module["key"]


    # “Ventana” que se abre debajo con los dashboards del módulo seleccionado
    selected_key = st.session_state.get("selected_module")
    if selected_key is not None:
        selected_module = next(
            (m for m in MODULES if m["key"] == selected_key),
            None,
        )
        if selected_module:
            with st.container(border=True):
                st.markdown(
                    f"<p style='font-size: 2.4vh; font-weight: 300; color: #fff;'>"
                    f"Dashboards disponibles en <b>{selected_module['title']}</b>"
                    f"</p>",
                    unsafe_allow_html=True,
                )
                # Botones de dashboards con expanders
                for dash in selected_module["dashboards"]:
                    with st.expander(dash):
                        # Aquí ponemos la descripción de cada dashboard desde el diccionario
                        st.write(DASHBOARD_INFO[dash])


# --------- COLUMNA DERECHA: MAPA + ALERTAS ---------
with columna2:
    with st.container(border=True):
        st.markdown(
            "<p style='font-size: 2.5vh; font-weight: 300; color: #fff;'>"
            "Previsualización del dashboard seleccionado</p>",
            unsafe_allow_html=True,
        )
        # Carga del shp
        gdf = load_gdf_wgs84(shp_path)
        geojson_str, bounds, name_col = make_geojson_simplified(gdf, tol_m=200)
        minx, miny, maxx, maxy = bounds
        center_lat = (miny + maxy) / 2
        center_lon = (minx + maxx) / 2

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=3,
            tiles="cartodbpositron",
            prefer_canvas=True,
            control_scale=False,
            zoom_control=False,
        )

        m.get_root().html.add_child(
            folium.Element(
                """
                <style>
                .leaflet-control-attribution {display:none !important;}
                .leaflet-container a {display:none !important;}
                </style>
                """
            )
        )

        folium.GeoJson(
            data=geojson_str,
            name="Regiones",
            smooth_factor=0.8,
            tooltip=folium.GeoJsonTooltip(
                fields=[name_col],
                aliases=["Región:"],
                sticky=True,
            ),
            style_function=lambda _ : {
                "color": "#175CA1",
                "weight": 1.1,
                "opacity": 1,
                "fill": True,
                "fillColor": "#07A9E0",
                "fillOpacity": 0.15,
            },
        ).add_to(m)

        m.fit_bounds([[miny, minx], [maxy, maxx]])
        st_folium(m, height=420, width=None)

    with st.container(border=True):
        st.markdown(
            "<p style='font-size: 2.5vh; font-weight: 300; color: #fff;'>"
            "Alertas y Actualizaciones</p>",
            unsafe_allow_html=True,
        )
        alerta1 = st.checkbox("Agua Potable - Actualización Datos 2025", value=False)
        alerta2 = st.checkbox("Energía Renovable - Datos Eólica [Nuevo]", value=False)
        alerta4 = st.checkbox("Salud Pública - Actualización Datos 2024", value=False)

