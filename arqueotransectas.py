from qgis.PyQt.QtWidgets import QAction, QMessageBox, QInputDialog
from qgis.core import (
    QgsProject,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsField,
    QgsFields,
    Qgis,
)
from qgis.gui import QgsMapToolEmitPoint
from PyQt5.QtCore import QVariant

class ArqueoTransectas:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()

    def initGui(self):
        self.action = QAction("ArqueoTransectas: Generar Líneas", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("Herramientas", self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("Herramientas", self.action)

    def run(self):
        opciones_limites = ["Polígono existente", "Dibujo en canvas", "Extensión de pantalla"]
        fuente_limites, ok = QInputDialog.getItem(
            None, "Seleccionar límites", "Elige cómo definir los límites:", opciones_limites, 0, False
        )

        if not ok:
            QMessageBox.warning(None, "Cancelado", "Operación cancelada por el usuario")
            return

        opciones_direccion = ["vertical", "horizontal"]
        direccion, ok = QInputDialog.getItem(
            None, "Seleccionar dirección", "Elige la dirección de las líneas:", opciones_direccion, 0, False
        )

        if not ok:
            QMessageBox.warning(None, "Cancelado", "Operación cancelada por el usuario")
            return

        distancia, ok = QInputDialog.getDouble(
            None, "Distancia entre líneas", "Ingresa la distancia entre líneas:", 100, 1, 10000, 1
        )

        if not ok:
            QMessageBox.warning(None, "Cancelado", "Operación cancelada por el usuario")
            return

        # Obtener la geometría del área según la fuente seleccionada
        if fuente_limites == "Polígono existente":
            area_layer = self.iface.activeLayer()
            if not area_layer or area_layer.geometryType() != QgsWkbTypes.PolygonGeometry:
                QMessageBox.critical(None, "Error", "Selecciona una capa de polígonos como área de trabajo")
                return

            area_feature = next(area_layer.getFeatures(), None)
            if not area_feature:
                QMessageBox.critical(None, "Error", "La capa no tiene polígonos")
                return

            area_geom = area_feature.geometry()

        elif fuente_limites == "Dibujo en canvas":
            area_geom = self.dibujar_poligono()
            if not area_geom:
                QMessageBox.critical(None, "Error", "No se dibujó un área válida")
                return

        elif fuente_limites == "Extensión de pantalla":
            rect = self.iface.mapCanvas().extent()
            xmin, xmax, ymin, ymax = rect.xMinimum(), rect.xMaximum(), rect.yMinimum(), rect.yMaximum()
            area_geom = QgsGeometry.fromPolygonXY([[QgsPointXY(xmin, ymin), QgsPointXY(xmin, ymax), QgsPointXY(xmax, ymax), QgsPointXY(xmax, ymin), QgsPointXY(xmin, ymin)]])

        # Crear una nueva capa para las líneas
        crs = self.iface.mapCanvas().mapSettings().destinationCrs().toWkt()
        line_layer = QgsVectorLayer(f"LineString?crs={crs}", "Transectas", "memory")
        line_provider = line_layer.dataProvider()

        fields = QgsFields()
        fields.append(QgsField("ID", QVariant.Int))
        line_provider.addAttributes(fields)
        line_layer.updateFields()

        # Generar líneas dentro del área definida
        bounds = area_geom.boundingBox()
        xmin, xmax = bounds.xMinimum(), bounds.xMaximum()
        ymin, ymax = bounds.yMinimum(), bounds.yMaximum()

        line_features = []
        id_linea = 1

        if direccion == "vertical":
            x = xmin
            while x <= xmax:
                line = QgsGeometry.fromPolylineXY([QgsPointXY(x, ymin), QgsPointXY(x, ymax)])
                line_clipped = line.intersection(area_geom)
                if line_clipped:
                    feature = QgsFeature(fields)
                    feature.setGeometry(line_clipped)
                    feature.setAttributes([id_linea])
                    line_features.append(feature)
                    id_linea += 1
                x += distancia
        elif direccion == "horizontal":
            y = ymin
            while y <= ymax:
                line = QgsGeometry.fromPolylineXY([QgsPointXY(xmin, y), QgsPointXY(xmax, y)])
                line_clipped = line.intersection(area_geom)
                if line_clipped:
                    feature = QgsFeature(fields)
                    feature.setGeometry(line_clipped)
                    feature.setAttributes([id_linea])
                    line_features.append(feature)
                    id_linea += 1
                y += distancia

        line_provider.addFeatures(line_features)
        QgsProject.instance().addMapLayer(line_layer)

        QMessageBox.information(None, "Éxito", "Transectas generadas correctamente")

    def dibujar_poligono(self):
        puntos = []

        class HerramientaDibujo(QgsMapToolEmitPoint):
            def __init__(self, canvas, puntos):
                super().__init__(canvas)
                self.canvas = canvas
                self.puntos = puntos
                self.terminado = False

            def canvasReleaseEvent(self, event):
                punto = self.toMapCoordinates(event.pos())
                self.puntos.append(QgsPointXY(punto))
                if len(self.puntos) > 2 and event.button() == 2:  # Botón derecho para finalizar
                    self.terminado = True
                    self.canvas.unsetMapTool(self)
                    QMessageBox.information(None, "Dibujo", "Polígono terminado")

        herramienta = HerramientaDibujo(self.canvas, puntos)
        self.canvas.setMapTool(herramienta)

        while not herramienta.terminado:
            QCoreApplication.processEvents()

        if len(puntos) > 2:
            puntos.append(puntos[0])  # Cerrar el polígono
            return QgsGeometry.fromPolygonXY([puntos])
        else:
            return None
