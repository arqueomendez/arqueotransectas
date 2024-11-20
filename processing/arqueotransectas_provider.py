from qgis.core import QgsProcessingProvider
from .arqueotransectas_algorithm import ArqueoTransectasAlgorithm


class ArqueoTransectasProvider(QgsProcessingProvider):
    """
    Clase que registra los algoritmos del complemento en el marco de procesamiento.
    """

    def loadAlgorithms(self):
        """
        Registra el algoritmo ArqueoTransectas.
        """
        self.addAlgorithm(ArqueoTransectasAlgorithm())

    def id(self):
        """
        Identificador del proveedor.
        """
        return "arqueotransectas_provider"

    def name(self):
        """
        Nombre corto del proveedor.
        """
        return "ArqueoTransectas"

    def longName(self):
        """
        Nombre largo del proveedor.
        """
        return "Proveedor de ArqueoTransectas"
