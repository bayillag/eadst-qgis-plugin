def classFactory(iface):
    from .main_plugin import EADSTPlugin
    return EADSTPlugin(iface)
