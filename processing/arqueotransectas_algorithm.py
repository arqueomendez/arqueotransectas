from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsFeatureSink,
    QgsProcessingException,
    QgsGeometry,
    QgsFeature,
    QgsPointXY,
    Qgis,
)


class ArqueoTransectasAlgorithm(QgsProcessingAlgorithm):
    """
    Algoritmo para generar transectas arqueológicas.
    """

    INPUT_LAYER = "INPUT_LAYER"
    TRANSECT_DIRECTION = "TRANSECT_DIRECTION"
    LINE_SPACING = "LINE_SPACING"
    OUTPUT_LAYER = "OUTPUT_LAYER"

    def initAlgorithm(self, config=None):
        """
        Definición de los parámetros del algoritmo.
        """
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                "Selecciona una capa de polígonos",
                [Qgis.ProcessingSourceType.TypeVectorPolygon],
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.TRANSECT_DIRECTION,
                "Dirección de las transectas",
                options=["Vertical", "Horizontal"],
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.LINE_SPACING,
                "Distancia entre líneas (en unidades de mapa)",
                Qgis.ProcessingNumberParameterType.Double,
                100,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_LAYER, "Capa de salida (transectas)"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Ejecución del algoritmo.
        """
        input_layer = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        direction = self.parameterAsEnum(parameters, self.TRANSECT_DIRECTION, context)
        spacing = self.parameterAsDouble(parameters, self.LINE_SPACING, context)

        if not input_layer:
            raise QgsProcessingException("No se pudo cargar la capa de entrada.")

        (sink, sink_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT_LAYER,
            context,
            input_layer.fields(),
            Qgis.WkbType.LineString,
            input_layer.sourceCrs(),
        )

        if sink is None:
            raise QgsProcessingException("No se pudo crear la capa de salida.")

        for feature in input_layer.getFeatures():
            geom = feature.geometry()
            bounds = geom.boundingBox()
            xmin, xmax = bounds.xMinimum(), bounds.xMaximum()
            ymin, ymax = bounds.yMinimum(), bounds.yMaximum()

            if direction == 0:  # Vertical
                x = xmin
                while x <= xmax:
                    line = QgsGeometry.fromPolylineXY(
                        [QgsPointXY(x, ymin), QgsPointXY(x, ymax)]
                    )
                    line_clipped = line.intersection(geom)
                    if (
                        not line_clipped.isEmpty()
                        and line_clipped.type() == Qgis.GeometryType.Line
                    ):
                        transect_feature = QgsFeature()
                        transect_feature.setGeometry(line_clipped)
                        sink.addFeature(
                            transect_feature, QgsFeatureSink.Flag.FastInsert
                        )
                    x += spacing
            else:  # Horizontal
                y = ymin
                while y <= ymax:
                    line = QgsGeometry.fromPolylineXY(
                        [QgsPointXY(xmin, y), QgsPointXY(xmax, y)]
                    )
                    line_clipped = line.intersection(geom)
                    if (
                        not line_clipped.isEmpty()
                        and line_clipped.type() == Qgis.GeometryType.Line
                    ):
                        transect_feature = QgsFeature()
                        transect_feature.setGeometry(line_clipped)
                        sink.addFeature(
                            transect_feature, QgsFeatureSink.Flag.FastInsert
                        )
                    y += spacing

        return {self.OUTPUT_LAYER: sink_id}

    def name(self):
        return "arqueotransectas"

    def displayName(self):
        return "Generar Líneas"

    def group(self):
        return ""

    def groupId(self):
        return ""

    def shortHelpString(self):
        return (
            "Generates evenly spaced transect lines (vertical or horizontal) clipped "
            "to the boundary of one or more input polygons."
            "<br><br>"
            "<b>Parameters</b>"
            "<br><br>"
            "<b>Input polygon layer</b>: Vector layer containing the area(s) within "
            "which transects will be generated. Must be a polygon layer."
            "<br><br>"
            "<b>Transect direction</b>:<br>"
            "- <i>Vertical</i>: lines run from bottom to top of each polygon's bounding box.<br>"
            "- <i>Horizontal</i>: lines run from left to right."
            "<br><br>"
            "<b>Line spacing</b>: Distance between consecutive transect lines, in the "
            "map units of the input layer's CRS."
            "<br><br>"
            "<b>Output layer</b>: LineString layer containing the clipped transect lines. "
            "Each transect is stored as a separate feature."
            "<br><br>"
            "<b>Notes</b><br>"
            "- Transects are clipped to the exact polygon boundary, not the bounding box.<br>"
            "- If a transect only grazes a polygon vertex, it is automatically discarded.<br>"
            "- For best results, ensure the input layer uses a projected CRS (metres or "
            "feet) so that the spacing value is meaningful."
            "<br><br>"
            "<b>Citation</b><br>"
            "If you use this plugin in your research or project, please cite it as:<br>"
            "<a href='https://github.com/arqueomendez/arqueotransectas'>"
            "https://github.com/arqueomendez/arqueotransectas</a>"
        )

    def createInstance(self):
        return ArqueoTransectasAlgorithm()
