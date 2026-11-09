"""Build maps of casualty accidents and road width in urban Estonia.

Loads the accident points from a CSV file and the roads from a GeoPackage
file, styles both layers and exports one PNG map for each area in AREAS.

Before running:
    1. Set BASE_DIR to the folder where this repository was cloned.
    2. Run download_roads.py once to create data/roads.gpkg.
    3. Set the map areas in AREAS (west, south, east, north in EPSG:3301).

How to run: in QGIS open Plugins > Python Console > Show Editor, open this
file and press the green Run button. The maps are saved in the images folder.
"""

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

# Zoom the main QGIS window to the area you want (Estonia, Tartu or Tallinn), then run this in the Python console or editor:
# e = iface.mapCanvas().extent()
# print(e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum())

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



def load_points(csv_path):
    """Load the accident CSV as a point layer.

    In Estonian coordinates X is north and Y is east, so the QGIS X field is
    set to y_coord and the QGIS Y field to x_coord.

    Args:
        csv_path: Path to accidents_cleaned.csv.

    Returns:
        A QgsVectorLayer with the accident points (EPSG:3301).
    """
    uri = (QUrl.fromLocalFile(csv_path).toString()
           + "?type=csv&delimiter=,&detectTypes=yes"
           + "&xField=y_coord&yField=x_coord&crs=EPSG:3301")
    return QgsVectorLayer(uri, "accidents_cleaned", "delimitedtext")


def load_roads(gpkg_path):
    """Load the road layer from the local GeoPackage file.

    Args:
        gpkg_path: Path to roads.gpkg (created by download_roads.py).

    Returns:
        A QgsVectorLayer with the road lines.
    """
    return QgsVectorLayer(gpkg_path + "|layername=roads", "roads", "ogr")



def style_roads(roads):
    """Style roads as grey lines whose thickness grows with road width.

    Uses the width classes in ROAD_CLASSES and the 'width' field.

    Args:
        roads: The road layer to style (changed in place).
    """
    ranges = []
    for lower, upper, label, line_width in ROAD_CLASSES:
        symbol = QgsSymbol.defaultSymbol(roads.geometryType())
        symbol.setColor(QColor("#999999"))
        symbol.setWidth(line_width)
        ranges.append(QgsRendererRange(lower, upper, symbol, label))
    roads.setRenderer(QgsGraduatedSymbolRenderer("width", ranges))


def style_points(points):
    """Style accidents as small semi-transparent red points.

    Args:
        points: The accident layer to style (changed in place).
    """
    symbol = QgsMarkerSymbol.createSimple({
        "name": "circle",
        "color": "255,0,51,110",
        "outline_color": "120,0,20,255",
        "outline_width": "0.1",
        "size": "1.2",
    })
    points.setRenderer(QgsSingleSymbolRenderer(symbol))



def fit_aspect(extent, ratio):
    """Grow an area until its width divided by its height equals ratio.

    The centre stays the same. Used to give the city maps the same shape.

    Args:
        extent: A QgsRectangle with the wanted area.
        ratio: Wanted width divided by height, for example 1.4.

    Returns:
        A new QgsRectangle with the adjusted area.
    """
    c = extent.center()
    w, h = extent.width(), extent.height()
    if w / h < ratio:
        w = h * ratio
    else:
        h = w / ratio
    return QgsRectangle(c.x() - w / 2, c.y() - h / 2, c.x() + w / 2, c.y() + h / 2)


def export_map(layers, extent, out_file, width_px=3000):
    """Render layers inside an area and save the result as a PNG file.

    Args:
        layers: List of layers to draw. The first layer is drawn on top.
        extent: A QgsRectangle with the area to draw.
        out_file: Path of the PNG file to write.
        width_px: Width of the image in pixels. The height follows the
            shape of the area.
    """
    settings = QgsMapSettings()
    settings.setLayers(layers)               
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
