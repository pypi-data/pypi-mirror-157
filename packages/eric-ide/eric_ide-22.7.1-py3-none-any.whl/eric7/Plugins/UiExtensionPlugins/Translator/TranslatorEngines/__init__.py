# -*- coding: utf-8 -*-

# Copyright (c) 2014 - 2022 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Package containing the various translation engines.
"""

import os

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIcon

from EricWidgets.EricApplication import ericApp

import UI.PixmapCache


def supportedEngineNames():
    """
    Module function to get the list of supported translation engines.
    
    @return names of supported engines
    @rtype list of str
    """
    return [
        "deepl", "googlev1", "googlev2", "ibm_watson", "microsoft", "mymemory",
        "yandex",
    ]


def engineDisplayName(name):
    """
    Module function to get a translated name for an engine.
    
    @param name name of a translation engine
    @type str
    @return translated engine name
    @rtype str
    """
    return {
        "deepl":
            QCoreApplication.translate("TranslatorEngines", "DeepL"),
        "googlev1":
            QCoreApplication.translate("TranslatorEngines", "Google V.1"),
        "googlev2":
            QCoreApplication.translate("TranslatorEngines", "Google V.2"),
        "ibm_watson":
            QCoreApplication.translate("TranslatorEngines", "IBM Watson"),
        "microsoft":
            QCoreApplication.translate("TranslatorEngines", "Microsoft"),
        "mymemory":
            QCoreApplication.translate("TranslatorEngines", "MyMemory"),
        "yandex":
            QCoreApplication.translate("TranslatorEngines", "Yandex"),
    }.get(
        name,
        QCoreApplication.translate(
            "TranslatorEngines", "Unknow translation service name ({0})"
        ).format(name)
    )


def getTranslationEngine(name, plugin, parent=None):
    """
    Module function to instantiate an engine object for the named service.
    
    @param name name of the online translation service
    @type str
    @param plugin reference to the plugin object
    @type TranslatorPlugin
    @param parent reference to the parent object
    @type QObject
    @return translation engine
    @rtype TranslatorEngine
    """
    if name == "deepl":
        from .DeepLEngine import DeepLEngine
        engine = DeepLEngine(plugin, parent)
    elif name == "googlev1":
        from .GoogleV1Engine import GoogleV1Engine
        engine = GoogleV1Engine(plugin, parent)
    elif name == "googlev2":
        from .GoogleV2Engine import GoogleV2Engine
        engine = GoogleV2Engine(plugin, parent)
    elif name == "ibm_watson":
        from .IbmWatsonEngine import IbmWatsonEngine
        engine = IbmWatsonEngine(plugin, parent)
    elif name == "microsoft":
        from .MicrosoftEngine import MicrosoftEngine
        engine = MicrosoftEngine(plugin, parent)
    elif name == "mymemory":
        from .MyMemoryEngine import MyMemoryEngine
        engine = MyMemoryEngine(plugin, parent)
    elif name == "yandex":
        from .YandexEngine import YandexEngine
        engine = YandexEngine(plugin, parent)
    else:
        engine = None
    return engine


def getEngineIcon(name):
    """
    Module function to get the icon of the named engine.
    
    @param name name of the translation engine
    @type str
    @return engine icon
    @rtype QIcon
    """
    iconSuffix = "dark" if ericApp().usesDarkPalette() else "light"
    if name in supportedEngineNames():
        icon = UI.PixmapCache.getIcon(os.path.join(
            os.path.dirname(__file__), "..", "icons", "engines",
            "{0}-{1}".format(name, iconSuffix)))
        if icon.isNull():
            # try variant without suffix
            icon = UI.PixmapCache.getIcon(os.path.join(
                os.path.dirname(__file__), "..", "icons", "engines",
                "{0}".format(name)))
        return icon
    else:
        return QIcon()


def getKeyUrl(name):
    """
    Module function to get an URL to request a user key.
    
    @param name name of the online translation service
    @type str
    @return key request URL
    @rtype str
    """
    return {
        "deepl":
            "https://www.deepl.com/de/pro-api",
        "googlev2":
            "https://console.developers.google.com/",
        "ibm_watson":
            "https://www.ibm.com/watson/services/language-translator/",
        "microsoft":
            "https://portal.azure.com",
        "mymemory":
            "http://mymemory.translated.net/doc/keygen.php",
        "yandex":
            "http://api.yandex.com/key/form.xml?service=trnsl",
    }.get(name, "")
