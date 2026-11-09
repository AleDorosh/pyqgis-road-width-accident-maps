points = QgsProject.instance().mapLayersByName("accidents_cleaned")[0]

# A simple round marker. Colours are written as "red,green,blue,alpha" (0-255).
# The last number is transparency: 255 is solid, lower is more see-through.
symbol = QgsMarkerSymbol.createSimple({
    "name": "circle",
    "color": "255,0,51,110",          # red, semi-transparent
    "outline_color": "120,0,20,255",  # dark red outline
    "outline_width": "0.1",           # thin outline, in mm
    "size": "1.2",                    # point size, in mm
})

points.setRenderer(QgsSingleSymbolRenderer(symbol))
points.triggerRepaint()