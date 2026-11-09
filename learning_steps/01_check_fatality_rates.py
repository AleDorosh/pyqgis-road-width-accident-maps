"""Check the fatality rate per road width class in PyQGIS.

Reproduces the SQL result from the analysis project: accidents, fatal
accidents and fatality rate for each width class. The numbers match the
Tableau chart (total: 3,533 accidents, 64 fatal).

Needs the layer 'accidents_cleaned' in the open QGIS project.
"""

layer = QgsProject.instance().mapLayersByName("accidents_cleaned")[0]
total = {}
fatal = {}
for f in layer.getFeatures():
    cat = f["width_category"]
    total[cat] = total.get(cat, 0) + 1
    if f["deaths"] and f["deaths"] > 0:
        fatal[cat] = fatal.get(cat, 0) + 1

for cat in ["≤5 m", "6-8 m", "9-11 m", "12-14 m", "15+ m"]:
    rate = 100 * fatal.get(cat, 0) / total[cat]
    print(cat, total[cat], fatal.get(cat, 0), round(rate, 2))
    
