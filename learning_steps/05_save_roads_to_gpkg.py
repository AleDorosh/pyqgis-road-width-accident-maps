
import os

roads = QgsProject.instance().mapLayersByName(
    "TN_transportetak:TN.RoadTransportNetwork.Roadwidth")[0]

gpkg = os.path.expanduser("~/pyqgis_maps/roads.gpkg")
os.makedirs(os.path.dirname(gpkg), exist_ok=True)

# "native:savefeatures" is the same tool as Export > Save Features As
result = processing.run("native:savefeatures", {
    "INPUT": roads,
    "OUTPUT": gpkg,
    "LAYER_NAME": "roads",     # the layer name inside the file
})
print("Saved:", result["OUTPUT"])
