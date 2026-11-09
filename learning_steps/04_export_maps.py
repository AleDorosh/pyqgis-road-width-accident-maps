"""Export PNG maps for Estonia, Tartu and Tallinn from the open QGIS project.

Uses layers that are already styled in the project. Fill in AREAS (west,
south, east, north in EPSG:3301) before running. The maps are saved in the
folder pyqgis_maps in the home folder.
"""

import os
from qgis.core import QgsMapSettings, QgsMapRendererParallelJob, QgsRectangle
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtGui import QColor

roads = QgsProject.instance().mapLayersByName(
    "TN_transportetak:TN.RoadTransportNetwork.Roadwidth")[0]
points = QgsProject.instance().mapLayersByName("accidents_cleaned")[0]

out_dir = os.path.expanduser("~/pyqgis_maps")
os.makedirs(out_dir, exist_ok=True)

# name: (west, south, east, north) -- paste your own numbers
areas = {
    "estonia": (358338.9516526179, 6370135.354926471, 745768.1126428994, 6623499.851976518),
    "tartu":   (653967.7769547486, 6469558.034530824, 666074.9382356949, 6477475.675063638),
    "tallinn": (520475.2502091928, 6573262.515076004, 568903.895332978, 6604933.07720726),
}

def fit_aspect(extent, ratio):
    # Grow the area until width / height equals ratio, keeping the centre.
    # This makes the city maps the same shape.
    c = extent.center()
    w, h = extent.width(), extent.height()
    if w / h < ratio:
        w = h * ratio
    else:
        h = w / ratio
    return QgsRectangle(c.x() - w / 2, c.y() - h / 2, c.x() + w / 2, c.y() + h / 2)

def export_map(extent, out_file, width_px=3000):
    settings = QgsMapSettings()
    settings.setLayers([points, roads])      # first in the list is drawn on top
    settings.setBackgroundColor(QColor("white"))
    settings.setDestinationCrs(points.crs())
    settings.setExtent(extent)
    settings.setOutputDpi(300)
    height_px = int(width_px * extent.height() / extent.width())
    settings.setOutputSize(QSize(width_px, height_px))
    job = QgsMapRendererParallelJob(settings)
    job.start()
    job.waitForFinished()
    job.renderedImage().save(out_file)
    print("Saved:", out_file)

for name, (xmin, ymin, xmax, ymax) in areas.items():
    extent = QgsRectangle(xmin, ymin, xmax, ymax)
    if name != "estonia":
        extent = fit_aspect(extent, 1.4)     # same shape for both city maps
    export_map(extent, os.path.join(out_dir, f"map_{name}.png"))
