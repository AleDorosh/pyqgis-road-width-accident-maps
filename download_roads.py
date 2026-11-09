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
