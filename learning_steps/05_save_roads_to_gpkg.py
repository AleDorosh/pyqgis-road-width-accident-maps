"""Save the WFS road layer from the open QGIS project to a GeoPackage.

First version of the download step. Replaced by download_roads.py, which
creates the WFS layer in code and needs no open project.
"""

import os

roads = QgsProject.instance().mapLayersByName(
    "TN_transportetak:TN.RoadTransportNetwork.Roadwidth")[0]

gpkg = os.path.expanduser("~/path/to/pyqgis-road-width-accident-maps")
os.makedirs(os.path.dirname(gpkg), exist_ok=True)

# "native:savefeatures" is the same tool as Export > Save Features As
result = processing.run("native:savefeatures", {
    "INPUT": roads,
    "OUTPUT": gpkg,
    "LAYER_NAME": "roads",     # the layer name inside the file
})
print("Saved:", result["OUTPUT"])
