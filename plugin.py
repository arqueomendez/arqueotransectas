from qgis.PyQt.QtWidgets import QAction, QMessageBox
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
        # Crear la acción del complemento
        self.plugin_action = QAction("ArqueoTransectas: Generar Líneas", self.iface.mainWindow())
        self.plugin_action.triggered.connect(self.show_help)
        self.iface.addToolBarIcon(self.plugin_action)
        self.iface.addPluginToMenu("Herramientas", self.plugin_action)

        # Registrar el proveedor de algoritmos
        self.provider = ArqueoTransectasProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """
        Método para limpiar el complemento al desactivarlo.
        """
        self.iface.removeToolBarIcon(self.plugin_action)
        self.iface.removePluginMenu("Herramientas", self.plugin_action)

        # Eliminar el proveedor
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

    def show_help(self):
        """
        Método que muestra un mensaje informativo al usuario.
        """
        QMessageBox.information(
            None,
            "Información",
            "Este complemento genera transectas arqueológicas.\n"
            "Encuentra el algoritmo en la Caja de herramientas de procesamiento.",
        )
