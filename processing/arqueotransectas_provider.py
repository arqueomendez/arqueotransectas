from qgis.core import QgsProcessingProvider
from .arqueotransectas_algorithm import ArqueoTransectasAlgorithm


class ArqueoTransectasProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        self.addAlgorithm(ArqueoTransectasAlgorithm())

    def id(self):
        return "arqueotransectas_provider"

    def name(self):
        return "ArqueoTransectas"

    def longName(self):
        return "Proveedor de ArqueoTransectas"
