from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsFeatureSink,
    QgsProcessingContext,
    QgsProcessingException,
    QgsGeometry,
    QgsFeature,
    QgsPointXY,
    QgsWkbTypes,
)


class ArqueoTransectasAlgorithm(QgsProcessingAlgorithm):
    INPUT_LAYER = "INPUT_LAYER"
    TRANSECT_DIRECTION = "TRANSECT_DIRECTION"
    LINE_SPACING = "LINE_SPACING"
    OUTPUT_LAYER = "OUTPUT_LAYER"

    def initAlgorithm(self, config=None):
        # Definir los parámetros del algoritmo
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER, "Selecciona una capa de polígonos", [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TRANSECT_DIRECTION, "Dirección de las transectas", options=["Vertical", "Horizontal"], defaultValue=0
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.LINE_SPACING, "Distancia entre líneas (en unidades de mapa)", QgsProcessingParameterNumber.Double, 100
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT_LAYER, "Capa de salida (transectas)")
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Leer los parámetros de entrada
        input_layer = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        direction = self.parameterAsEnum(parameters, self.TRANSECT_DIRECTION, context)
        spacing = self.parameterAsDouble(parameters, self.LINE_SPACING, context)

        if not input_layer:
            raise QgsProcessingException("No se pudo cargar la capa de entrada.")

        # Crear la capa de salida
        (sink, sink_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_LAYER,
            context,
            input_layer.fields(),
            QgsWkbTypes.LineString,
            input_layer.sourceCrs(),
        )

        if sink is None:
            raise QgsProcessingException("No se pudo crear la capa de salida.")

        # Generar las transectas
        for feature in input_layer.getFeatures():
            geom = feature.geometry()
            bounds = geom.boundingBox()
            xmin, xmax = bounds.xMinimum(), bounds.xMaximum()
            ymin, ymax = bounds.yMinimum(), bounds.yMaximum()

            if direction == 0:  # Vertical
                x = xmin
                while x <= xmax:
                    line = QgsGeometry.fromPolylineXY([QgsPointXY(x, ymin), QgsPointXY(x, ymax)])
                    line_clipped = line.intersection(geom)
                    if line_clipped:
                        transect_feature = QgsFeature()
                        transect_feature.setGeometry(line_clipped)
                        sink.addFeature(transect_feature, QgsFeatureSink.FastInsert)
                    x += spacing
            else:  # Horizontal
                y = ymin
                while y <= ymax:
                    line = QgsGeometry.fromPolylineXY([QgsPointXY(xmin, y), QgsPointXY(xmax, y)])
                    line_clipped = line.intersection(geom)
                    if line_clipped:
                        transect_feature = QgsFeature()
                        transect_feature.setGeometry(line_clipped)
                        sink.addFeature(transect_feature, QgsFeatureSink.FastInsert)
                    y += spacing

        return {self.OUTPUT_LAYER: sink_id}

    def name(self):
        return "arqueotransectas"

    def displayName(self):
        return "ArqueoTransectas: Generar Líneas"

    def group(self):
        return "Herramientas Personalizadas"

    def groupId(self):
        return "herramientas_personalizadas"

    def createInstance(self):
        return ArqueoTransectasAlgorithm()
