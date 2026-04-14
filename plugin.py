import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication

from .processing.arqueotransectas_provider import ArqueoTransectasProvider


class ArqueoTransectasPlugin:
    """
    Clase principal del complemento ArqueoTransectas.
    Maneja el registro del proveedor de algoritmos y la interfaz gráfica.
    """

    def __init__(self, iface):
        """
        Constructor de la clase del complemento.

        :param iface: Interfaz de QGIS (QgisInterface)
        """
        self.iface = iface
        self.plugin_action = None
        self.provider = None

    def initGui(self):
        """
        Método para inicializar la interfaz gráfica del complemento.
        """
        icon = QIcon(os.path.join(os.path.dirname(__file__), "icon.png"))

        self.plugin_action = QAction(
            icon,
            "Generar Líneas de Transecta",
            self.iface.mainWindow(),
        )
        self.plugin_action.setToolTip(
            "Genera transectas arqueológicas dentro de un área definida"
        )
        self.plugin_action.triggered.connect(self.run)

        # Aparece en Complementos → ArqueoTransectas → Generar Líneas de Transecta
        self.iface.addPluginToMenu("ArqueoTransectas", self.plugin_action)

        # Botón en la barra de herramientas
        self.iface.addToolBarIcon(self.plugin_action)

        # Registrar el proveedor en la Caja de herramientas de procesamiento
        self.provider = ArqueoTransectasProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """
        Método para limpiar el complemento al desactivarlo.
        """
        self.iface.removePluginMenu("ArqueoTransectas", self.plugin_action)
        self.iface.removeToolBarIcon(self.plugin_action)

        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

    def run(self):
        """
        Abre el diálogo del algoritmo directamente para su ejecución.
        """
        import processing

        processing.execAlgorithmDialog("arqueotransectas_provider:arqueotransectas")
