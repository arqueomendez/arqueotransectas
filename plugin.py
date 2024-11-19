from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.core import QgsApplication
from .processing.arqueotransectas_provider import ArqueoTransectasProvider


class ArqueoTransectasPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_action = None
        self.provider = None

    def initGui(self):
        # Crear la acción del complemento
        self.plugin_action = QAction("ArqueoTransectas: Generar Líneas", self.iface.mainWindow())
        self.plugin_action.triggered.connect(self.show_help)
        self.iface.addToolBarIcon(self.plugin_action)
        self.iface.addPluginToMenu("Herramientas", self.plugin_action)

        # Registrar el proveedor de algoritmos
        self.provider = ArqueoTransectasProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        self.iface.removeToolBarIcon(self.plugin_action)
        self.iface.removePluginMenu("Herramientas", self.plugin_action)

        # Eliminar el proveedor
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

    def show_help(self):
        QMessageBox.information(
            None,
            "Información",
            "Este complemento genera transectas arqueológicas. Encuentra el algoritmo en la Caja de herramientas de procesamiento.",
        )
