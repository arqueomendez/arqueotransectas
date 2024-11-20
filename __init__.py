def classFactory(iface):
    """
    Esta función es obligatoria para todos los complementos.
    Es la entrada principal del complemento desde QGIS.
    """
    from .plugin import ArqueoTransectasPlugin
    return ArqueoTransectasPlugin(iface)
