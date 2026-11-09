import os
from qgis.core import (
    QgsVectorLayer, QgsSymbol, QgsMarkerSymbol, QgsRendererRange,
    QgsGraduatedSymbolRenderer, QgsSingleSymbolRenderer, QgsMapSettings,
    QgsMapRendererParallelJob, QgsRectangle,
)
from qgis.PyQt.QtCore import QSize, QUrl
from qgis.PyQt.QtGui import QColor

BASE_DIR = os.path.expanduser("~/path/to/pyqgis-road-width-accident-maps")
CSV_PATH = os.path.join(BASE_DIR, "data", "accidents_cleaned.csv")
GPKG_PATH = os.path.join(BASE_DIR, "data", "roads.gpkg")
OUT_DIR = os.path.join(BASE_DIR, "images")

# name: (west, south, east, north)
AREAS = {
    "estonia": (358338.9516526179, 6370135.354926471, 745768.1126428994, 6623499.851976518),
    "tartu":   (653967.7769547486, 6469558.034530824, 666074.9382356949, 6477475.675063638),
    "tallinn": (520475.2502091928, 6573262.515076004, 568903.895332978, 6604933.07720726),
}

# (lower, upper, legend label, line width in mm)
ROAD_CLASSES = [
    (0, 5, "≤5 m", 0.07),
    (5, 8, "6 - 8 m", 0.15),
    (8, 11, "9 - 11 m", 0.25),
    (11, 14, "12 - 14 m", 0.35),
    (14, 80, "15+ m", 0.5),
]


# ---------- Loading ----------
def load_points(csv_path):
    # X is the east value (y_coord), Y is the north value (x_coord)
    uri = (QUrl.fromLocalFile(csv_path).toString()
           + "?type=csv&delimiter=,&detectTypes=yes"
           + "&xField=y_coord&yField=x_coord&crs=EPSG:3301")
    return QgsVectorLayer(uri, "accidents_cleaned", "delimitedtext")


def load_roads(gpkg_path):
    return QgsVectorLayer(gpkg_path + "|layername=roads", "roads", "ogr")


# ---------- Styling ----------
def style_roads(roads):
    ranges = []
    for lower, upper, label, line_width in ROAD_CLASSES:
        symbol = QgsSymbol.defaultSymbol(roads.geometryType())
        symbol.setColor(QColor("#999999"))
        symbol.setWidth(line_width)
        ranges.append(QgsRendererRange(lower, upper, symbol, label))
    roads.setRenderer(QgsGraduatedSymbolRenderer("width", ranges))


def style_points(points):
    symbol = QgsMarkerSymbol.createSimple({
        "name": "circle",
        "color": "255,0,51,110",
        "outline_color": "120,0,20,255",
        "outline_width": "0.1",
        "size": "1.2",
    })
    points.setRenderer(QgsSingleSymbolRenderer(symbol))


# ---------- Exporting ----------
def fit_aspect(extent, ratio):
    # Grow the area until width / height equals ratio, keeping the centre
    c = extent.center()
    w, h = extent.width(), extent.height()
    if w / h < ratio:
        w = h * ratio
    else:
        h = w / ratio
    return QgsRectangle(c.x() - w / 2, c.y() - h / 2, c.x() + w / 2, c.y() + h / 2)


def export_map(layers, extent, out_file, width_px=3000):
    settings = QgsMapSettings()
    settings.setLayers(layers)               # first in the list is drawn on top
    settings.setBackgroundColor(QColor("white"))
    settings.setDestinationCrs(layers[0].crs())
    settings.setExtent(extent)
    settings.setOutputDpi(300)
    height_px = int(width_px * extent.height() / extent.width())
    settings.setOutputSize(QSize(width_px, height_px))
    job = QgsMapRendererParallelJob(settings)
    job.start()
    job.waitForFinished()
    job.renderedImage().save(out_file)
    print("Saved:", out_file)


# ---------- Run ----------
points = load_points(CSV_PATH)
roads = load_roads(GPKG_PATH)

# Stop with a clear message if a file could not be loaded
for layer in (points, roads):
    if not layer.isValid():
        raise RuntimeError(f"Could not load layer: {layer.name()}")

style_roads(roads)
style_points(points)

os.makedirs(OUT_DIR, exist_ok=True)
for name, (xmin, ymin, xmax, ymax) in AREAS.items():
    extent = QgsRectangle(xmin, ymin, xmax, ymax)
    if name != "estonia":
        extent = fit_aspect(extent, 1.4)
    export_map([points, roads], extent, os.path.join(OUT_DIR, f"map_{name}.png"))
