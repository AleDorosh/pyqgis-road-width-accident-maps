"""Download the Estonian road width layer and save it as a GeoPackage.

Connects to the WFS service of Maa- ja Ruumiamet, downloads all roads once
and saves them to data/roads.gpkg. Nothing is downloaded if the file already
exists, unless OVERWRITE is True.

The download takes several minutes and the file is large, so roads.gpkg is
excluded from the repository in .gitignore.

Before running: set BASE_DIR to the folder where this repository was cloned.
How to run: in QGIS open Plugins > Python Console > Show Editor, open this
file and press the green Run button.
"""

import os

BASE_DIR = os.path.expanduser("~/path/to/pyqgis-road-width-accident-maps")
GPKG_PATH = os.path.join(BASE_DIR, "data", "roads.gpkg")
OVERWRITE = False   # True = download again even if the file exists

# The web address and settings of the road width service (Maa- ja Ruumiamet, CC BY 4.0)
WFS_URI = ("pagingEnabled='default' preferCoordinatesForWfsT11='false' "
           "restrictToRequestBBOX='1' srsname='EPSG:3301' "
           "typename='TN_transportetak:TN.RoadTransportNetwork.Roadwidth' "
           "url='https://inspire.geoportaal.ee/geoserver/TN_transportetak/wfs' "
           "version='auto'")

if os.path.exists(GPKG_PATH) and not OVERWRITE:
    print("File already exists, nothing to do:", GPKG_PATH)
else:
    roads = QgsVectorLayer(WFS_URI, "roads_wfs", "WFS")
    if not roads.isValid():
        raise RuntimeError("Could not connect to the WFS service. Check your internet connection.")

    os.makedirs(os.path.dirname(GPKG_PATH), exist_ok=True)
    print("Downloading all roads, this can take several minutes...")
    result = processing.run("native:savefeatures", {
        "INPUT": roads,
        "OUTPUT": GPKG_PATH,
        "LAYER_NAME": "roads",
    })
    print("Saved:", result["OUTPUT"])
