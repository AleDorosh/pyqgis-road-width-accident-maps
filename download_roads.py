import os
roads = QgsProject.instance().mapLayersByName(
    "TN_transportetak:TN.RoadTransportNetwork.Roadwidth")[0]
gpkg = os.path.expanduser("~/pyqgis_maps/roads.gpkg")

result = processing.run("native:savefeatures", {
    "INPUT": roads,
    "OUTPUT": gpkg,
    "LAYER_NAME": "roads",
})
print("Saved:", result["OUTPUT"])