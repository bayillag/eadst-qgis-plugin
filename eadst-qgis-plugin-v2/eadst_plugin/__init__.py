# -*- coding: utf-8 -*-
"""This script initializes the QGIS plugin"""

def classFactory(iface):
    """Load main_plugin class from file main_plugin.
    
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .main_plugin import EADSTPlugin
    return EADSTPlugin(iface)