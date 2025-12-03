import pandas as pd
from unidecode import unidecode
import plotly.graph_objects as go
import os, base64, mimetypes
import numpy as np
import streamlit as st
from typing import Optional 
import geopandas as gpd 
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.transform import Affine
import numpy as np
from matplotlib import cm as mpl_cm
from PIL import Image
from io import BytesIO



def img_to_data_uri(path: str) -> str:
    mime = "image/svg+xml" if path.lower().endswith(".svg") else "image/png"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("utf-8")

@st.cache_data(show_spinner=False)
def load_gdf_wgs84(path: str) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    gdf = gdf.set_crs(4326) if gdf.crs is None else gdf.to_crs(4326)
    return gdf

@st.cache_data(show_spinner=False)
def make_geojson_simplified(_gdf, tol_m: float = 200.0):
    """Devuelve (geojson_str, bounds, name_col) ya simplificado y en EPSG:4326."""
    gdfm = _gdf.to_crs(3857).copy()
    gdfm["geometry"] = gdfm.geometry.simplify(tolerance=tol_m, preserve_topology=True)
    gdfs = gdfm.to_crs(4326)

    name_col = "NOMB_UGER" if "NOMB_UGER" in gdfs.columns else gdfs.columns[0]
    bounds = list(gdfs.total_bounds)  # [minx, miny, maxx, maxy]

    # 👇 Esto convierte automáticamente cualquier objeto no serializable (p.ej., Timestamp) a str
    return gdfs.to_json(default=str), bounds, name_col



@st.cache_data(show_spinner=False)
def raster_to_datauri_bounds(path: str, max_size: int = 1024, cmap: str = "viridis",
                             vmin: float | None = None, vmax: float | None = None):
    """Abre un ráster (banda 1), lo reproyecta a EPSG:4326, lo reduce y devuelve (data_uri_png, bounds)."""
    with rasterio.open(path) as src:
        # VRT reproyectado a WGS84
        with WarpedVRT(src, crs="EPSG:4326", resampling=Resampling.bilinear) as vrt:
            # Tamaño destino manteniendo aspecto
            scale = min(1.0, max_size / max(vrt.width, vrt.height))
            out_w = max(1, int(vrt.width * scale))
            out_h = max(1, int(vrt.height * scale))

            # Leer banda 1 reescalada
            data = vrt.read(1, out_shape=(out_h, out_w)).astype("float32")

            # Transform del reescalado: T' = T * Scale(width/out_w, height/out_h)
            new_transform = vrt.transform * Affine.scale(vrt.width / out_w, vrt.height / out_h)

            # Bounds en lon/lat
            minx, miny = new_transform * (0, out_h)
            maxx, maxy = new_transform * (out_w, 0)
            bounds = [[miny, minx], [maxy, maxx]]

            # Normalización robusta y colormap
            if vmin is None or vmax is None:
                finite = np.isfinite(data)
                if not finite.any():
                    raise ValueError("La banda no tiene valores finitos")
                vmin = np.nanpercentile(data[finite], 2)
                vmax = np.nanpercentile(data[finite], 98)
                if vmin == vmax:
                    vmax = vmin + 1e-6

            norm = np.clip((data - vmin) / (vmax - vmin), 0, 1)
            cmap_fn = mpl_cm.get_cmap(cmap)
            rgba = (cmap_fn(norm) * 255).astype(np.uint8)  # [H,W,4]

            # Transparente donde no hay datos (NaN) o nodata
            mask = ~np.isfinite(data)
            rgba[..., 3][mask] = 0

            # A PNG + data URI
            im = Image.fromarray(rgba, mode="RGBA")
            buf = BytesIO()
            im.save(buf, format="PNG", optimize=True)
            data_uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

    return data_uri, bounds, float(vmin), float(vmax)
