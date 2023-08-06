# -*- coding: utf-8 -*-

# Copyright (c) 2017 - 2022 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the DeepL translation engine.
"""

import json

from PyQt6.QtCore import QUrl, QByteArray, QTimer

import Utilities

from .TranslationEngine import TranslationEngine


class DeepLEngine(TranslationEngine):
    """
    Class implementing the translation engine for the DeepL
    translation service.
    """
    TranslatorUrls = {
        "pro": "https://api.deepl.com/v2/translate",
        "free": "https://api-free.deepl.com/v2/translate",
    }
    MaxTranslationTextLen = 30 * 1024
    
    def __init__(self, plugin, parent=None):
        """
        Constructor
        
        @param plugin reference to the plugin object
        @type TranslatorPlugin
        @param parent reference to the parent object
        @type QObject
        """
        super().__init__(plugin, parent)
        
        QTimer.singleShot(0, self.availableTranslationsLoaded.emit)
    
    def engineName(self):
        """
        Public method to return the name of the engine.
        
        @return engine name
        @rtype str
        """
        return "deepl"
    
    def supportedLanguages(self):
        """
        Public method to get the supported languages.
        
        @return list of supported language codes
        @rtype list of str
        """
        return ["bg", "cs", "da", "de", "el", "en", "es", "et", "fi", "fr",
                "hu", "id", "it", "ja", "lt", "lv", "nl", "pl", "pt", "ro",
                "ru", "sk", "sl", "sv", "tr", "zh"]
    
    def getTranslation(self, requestObject, text, originalLanguage,
                       translationLanguage):
        """
        Public method to translate the given text.
        
        @param requestObject reference to the request object
        @type TranslatorRequest
        @param text text to be translated
        @type str
        @param originalLanguage language code of the original
        @type str
        @param translationLanguage language code of the translation
        @type str
        @return tuple of translated text and flag indicating success
        @rtype tuple of (str, bool)
        """
        if len(text) > self.MaxTranslationTextLen:
            return (
                self.tr("DeepL: Text to be translated exceeds the translation"
                        " limit of {0} characters.")
                .format(self.MaxTranslationTextLen),
                False
            )
        
        apiKey = self.plugin.getPreferences("DeeplKey")
        if not apiKey:
            return self.tr("A valid DeepL Pro key is required."), False
        
        params = QByteArray(
            "auth_key={0}&source_lang={1}&target_lang={2}&text=".format(
                apiKey, originalLanguage.upper(), translationLanguage.upper())
            .encode("utf-8"))
        encodedText = (
            QByteArray(Utilities.html_encode(text).encode("utf-8"))
            .toPercentEncoding()
        )
        request = params + encodedText
        translatorUrl = (
            DeepLEngine.TranslatorUrls["free"]
            if apiKey.endswith(":fx") else
            DeepLEngine.TranslatorUrls["pro"]
        )
        response, ok = requestObject.post(QUrl(translatorUrl), request)
        if ok:
            try:
                responseDict = json.loads(response)
            except ValueError:
                return self.tr("Invalid response received from DeepL"), False
            
            if "translations" not in responseDict:
                return self.tr("DeepL call returned an unknown result"), False
            
            translations = responseDict["translations"]
            if len(translations) == 0:
                return self.tr("<p>DeepL: No translation found</p>"), True
            
            # show sentence by sentence separated by a line
            result = (
                "<p>" +
                "<hr/>".join([t["text"] for t in translations]) +
                "</p>"
            )
        
        else:
            result = response
        return result, ok
