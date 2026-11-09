"""Style the road layer by width class, in code instead of by hand.

Applies a graduated renderer on the 'width' field with the same classes as
the SQL analysis (up to 5 m, 6-8 m, 9-11 m, 12-14 m, 15+ m). Wider roads get
thicker lines.

Needs the WFS road layer in the open QGIS project.
"""

roads = QgsProject.instance().mapLayersByName(
    "TN_transportetak:TN.RoadTransportNetwork.Roadwidth")[0]

# (lower, upper, legend label, line width in mm)
classes = [
    (0, 5, "≤5 m", 0.07),
    (5, 8, "6 - 8 m", 0.15),
    (8, 11, "9 - 11 m", 0.25),
    (11, 14, "12 - 14 m", 0.35),
    (14, 80, "15+ m", 0.5),
]

ranges = []
for lower, upper, label, line_width in classes:
    symbol = QgsSymbol.defaultSymbol(roads.geometryType())
    symbol.setColor(QColor("#999999"))
    symbol.setWidth(line_width)
    ranges.append(QgsRendererRange(lower, upper, symbol, label))

roads.setRenderer(QgsGraduatedSymbolRenderer("width", ranges))
roads.triggerRepaint()
