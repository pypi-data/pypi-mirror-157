# -*- coding: utf-8 -*-

# Copyright (c) 2013 - 2022 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the setup.py wizard dialog.
"""

import os
import datetime

import trove_classifiers

from PyQt6.QtCore import pyqtSlot, Qt
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QTreeWidgetItem, QListWidgetItem
)

from EricWidgets.EricApplication import ericApp
from EricWidgets import EricFileDialog
from EricWidgets.EricPathPicker import EricPathPickerModes

from .Ui_SetupWizardDialog import Ui_SetupWizardDialog

import Utilities
import Preferences


class SetupWizardDialog(QDialog, Ui_SetupWizardDialog):
    """
    Class implementing the setup.py wizard dialog.
    
    It displays a dialog for entering the parameters for the setup.py code
    generator.
    """
    def __init__(self, parent=None):
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super().__init__(parent)
        self.setupUi(self)
        
        self.__replies = []
        
        self.dataTabWidget.setCurrentIndex(0)
        
        self.packageRootPicker.setMode(EricPathPickerModes.DIRECTORY_MODE)
        self.sourceDirectoryPicker.setMode(EricPathPickerModes.DIRECTORY_MODE)
        
        self.__mandatoryStyleSheet = (
            "QLineEdit {border: 2px solid; border-color: #dd8888}"
            if ericApp().usesDarkPalette() else
            "QLineEdit {border: 2px solid; border-color: #800000}"
        )
        for lineEdit in [self.nameEdit, self.versionEdit,
                         self.homePageUrlEdit, self.authorEdit,
                         self.authorEmailEdit, self.maintainerEdit,
                         self.maintainerEmailEdit]:
            lineEdit.setStyleSheet(self.__mandatoryStyleSheet)
        
        self.__populateClassifiers()
        
        self.__okButton = self.buttonBox.button(
            QDialogButtonBox.StandardButton.Ok)
        self.__okButton.setEnabled(False)
        
        projectOpen = ericApp().getObject("Project").isOpen()
        self.projectButton.setEnabled(projectOpen)
        
        self.homePageUrlEdit.textChanged.connect(self.__enableOkButton)
        self.nameEdit.textChanged.connect(self.__enableOkButton)
        self.versionEdit.textChanged.connect(self.__enableOkButton)
        self.authorEdit.textChanged.connect(self.__enableOkButton)
        self.authorEmailEdit.textChanged.connect(self.__enableOkButton)
        self.maintainerEdit.textChanged.connect(self.__enableOkButton)
        self.maintainerEmailEdit.textChanged.connect(self.__enableOkButton)
    
    def __enableOkButton(self):
        """
        Private slot to set the state of the OK button.
        """
        enable = (
            bool(self.nameEdit.text()) and
            bool(self.versionEdit.text()) and
            bool(self.homePageUrlEdit.text()) and
            ((bool(self.authorEdit.text()) and
                bool(self.authorEmailEdit.text())) or
             (bool(self.maintainerEdit.text()) and
              bool(self.maintainerEmailEdit.text()))) and
            self.homePageUrlEdit.text().startswith(("http://", "https://"))
        )
        
        self.__okButton.setEnabled(enable)
    
    def __populateClassifiers(self):
        """
        Private method to populate the classifiers.
        """
        self.licenseClassifierComboBox.clear()
        self.classifiersList.clear()
        self.developmentStatusComboBox.clear()
        
        self.developmentStatusComboBox.addItem("", "")
        
        self.__classifiersDict = {}
        for classifier in trove_classifiers.sorted_classifiers:
            if classifier.startswith("License ::"):
                self.licenseClassifierComboBox.addItem(
                    "/".join(classifier.split(" :: ")[1:]),
                    classifier
                )
            elif classifier.startswith("Development Status ::"):
                self.developmentStatusComboBox.addItem(
                    classifier.split(" :: ")[1], classifier)
            else:
                self.__addClassifierEntry(classifier)
        self.__classifiersDict = {}
        
        self.licenseClassifierComboBox.setCurrentIndex(
            self.licenseClassifierComboBox.findText(
                "(GPLv3)",
                Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchCaseSensitive
            )
        )
    
    def __addClassifierEntry(self, classifier):
        """
        Private method to add a new entry to the list of trove classifiers.
        
        @param classifier classifier containing the data for the entry
        @type str
        """
        itm = None
        pitm = None
        dataList = classifier.split(" :: ")
        for index in range(len(dataList)):
            key = " :: ".join(dataList[:index + 1])
            if key not in self.__classifiersDict:
                if pitm is None:
                    itm = QTreeWidgetItem(
                        self.classifiersList, [dataList[index]])
                    pitm = itm
                else:
                    itm = QTreeWidgetItem(pitm, [dataList[index]])
                itm.setExpanded(True)
                self.__classifiersDict[key] = itm
            else:
                pitm = self.__classifiersDict[key]
        itm.setCheckState(0, Qt.CheckState.Unchecked)
        itm.setData(0, Qt.ItemDataRole.UserRole, classifier)
    
    def __getLicenseText(self):
        """
        Private method to get the license text.
        
        @return license text
        @rtype str
        """
        if not self.licenseClassifierCheckBox.isChecked():
            return self.licenseEdit.text()
        else:
            lic = self.licenseClassifierComboBox.currentText()
            if "(" in lic:
                lic = lic.rsplit("(", 1)[1].split(")", 1)[0]
            return lic
    
    def getCode(self, indLevel, indString):
        """
        Public method to get the source code.
        
        @param indLevel indentation level
        @type int
        @param indString string used for indentation (space or tab)
        @type str
        @return generated code
        @rtype str
        """
        # Note: all paths are created with '/'; setup will do the right thing
        
        # calculate our indentation level and the indentation string
        il = indLevel + 1
        istring = il * indString
        i1string = (il + 1) * indString
        i2string = (il + 2) * indString
        estring = os.linesep + indLevel * indString
        
        # now generate the code
        if self.introCheckBox.isChecked():
            sourceCode = "#!/usr/bin/env python3{0}".format(os.linesep)
            sourceCode += "# -*- coding: utf-8 -*-{0}{0}".format(os.linesep)
        else:
            sourceCode = ""
        
        if self.metaDataCheckBox.isChecked():
            sourceCode += '# metadata{0}'.format(os.linesep)
            sourceCode += '"{0}"{1}'.format(
                self.summaryEdit.text() or "Setup routine",
                os.linesep
            )
            sourceCode += '__version__ = "{0}"{1}'.format(
                self.versionEdit.text(), os.linesep)
            sourceCode += '__license__ = "{0}"{1}'.format(
                self.__getLicenseText(), os.linesep)
            sourceCode += '__author__ = "{0}"{1}'.format(
                self.authorEdit.text() or self.maintainerEdit.text(),
                os.linesep)
            sourceCode += '__email__ = "{0}"{1}'.format(
                self.authorEmailEdit.text() or self.maintainerEmailEdit.text(),
                os.linesep)
            sourceCode += '__url__ = "{0}"{1}'.format(
                self.homePageUrlEdit.text(), os.linesep)
            sourceCode += '__date__ = "{0}"{1}'.format(
                datetime.datetime.now().isoformat().split('.')[0], os.linesep)
            sourceCode += '__prj__ = "{0}"{1}'.format(
                self.nameEdit.text(), os.linesep)
            sourceCode += os.linesep
        
        if self.importCheckBox.isChecked():
            additionalImport = ", find_packages"
            sourceCode += "from setuptools import setup{0}{1}".format(
                additionalImport, os.linesep)
        if sourceCode:
            sourceCode += "{0}{0}".format(os.linesep)
        
        if self.descriptionFromFilesCheckBox.isChecked():
            sourceCode += 'def get_long_description():{0}'.format(os.linesep)
            sourceCode += '{0}descr = []{1}'.format(istring, os.linesep)
            sourceCode += '{0}for fname in "{1}":{2}'.format(
                istring,
                '", "'.join(self.descriptionEdit.toPlainText().splitlines()),
                os.linesep)
            sourceCode += '{0}{0}with open(fname) as f:{1}'.format(
                istring, os.linesep)
            sourceCode += '{0}{0}{0}descr.append(f.read()){1}'.format(
                istring, os.linesep)
            sourceCode += '{0}return "\\n\\n".join(descr){1}'.format(
                istring, os.linesep)
            sourceCode += "{0}{0}".format(os.linesep)
        
        sourceCode += 'setup({0}'.format(os.linesep)
        sourceCode += '{0}name="{1}",{2}'.format(
            istring, self.nameEdit.text(), os.linesep)
        sourceCode += '{0}version="{1}",{2}'.format(
            istring, self.versionEdit.text(), os.linesep)
        
        if self.summaryEdit.text():
            sourceCode += '{0}description="{1}",{2}'.format(
                istring, self.summaryEdit.text(), os.linesep)
        
        if self.descriptionFromFilesCheckBox.isChecked():
            sourceCode += '{0}long_description=get_long_description(),{1}'.format(
                istring, os.linesep)
        elif self.descriptionEdit.toPlainText():
            sourceCode += '{0}long_description="""{1}""",{2}'.format(
                istring, self.descriptionEdit.toPlainText(), os.linesep)
        
        if self.authorEdit.text():
            sourceCode += '{0}author="{1}",{2}'.format(
                istring, self.authorEdit.text(), os.linesep)
            sourceCode += '{0}author_email="{1}",{2}'.format(
                istring, self.authorEmailEdit.text(), os.linesep)
        
        if self.maintainerEdit.text():
            sourceCode += '{0}maintainer="{1}",{2}'.format(
                istring, self.maintainerEdit.text(), os.linesep)
            sourceCode += '{0}maintainer_email="{1}",{2}'.format(
                istring, self.maintainerEmailEdit.text(), os.linesep)
        
        sourceCode += '{0}url="{1}",{2}'.format(
            istring, self.homePageUrlEdit.text(), os.linesep)
        
        classifiers = []
        if not self.licenseClassifierCheckBox.isChecked():
            sourceCode += '{0}license="{1}",{2}'.format(
                istring, self.licenseEdit.text(), os.linesep)
        else:
            classifiers.append(
                self.licenseClassifierComboBox.itemData(
                    self.licenseClassifierComboBox.currentIndex()))
        
        platforms = self.platformsEdit.toPlainText().splitlines()
        if platforms:
            sourceCode += '{0}platforms=[{1}'.format(istring, os.linesep)
            sourceCode += '{0}"{1}"{2}'.format(
                i1string,
                '",{0}{1}"'.format(os.linesep, i1string).join(platforms),
                os.linesep)
            sourceCode += '{0}],{1}'.format(istring, os.linesep)
        
        if self.developmentStatusComboBox.currentIndex() != 0:
            classifiers.append(
                self.developmentStatusComboBox.itemData(
                    self.developmentStatusComboBox.currentIndex()))
        
        itm = self.classifiersList.topLevelItem(0)
        while itm:
            itm.setExpanded(True)
            if itm.checkState(0) == Qt.CheckState.Checked:
                classifiers.append(itm.data(0, Qt.ItemDataRole.UserRole))
            itm = self.classifiersList.itemBelow(itm)
        
        # cleanup classifiers list - remove all invalid entries
        classifiers = [c for c in classifiers if bool(c)]
        if classifiers:
            sourceCode += '{0}classifiers=[{1}'.format(istring, os.linesep)
            sourceCode += '{0}"{1}"{2}'.format(
                i1string,
                '",{0}{1}"'.format(os.linesep, i1string).join(classifiers),
                os.linesep)
            sourceCode += '{0}],{1}'.format(istring, os.linesep)
        del classifiers
        
        if self.keywordsEdit.text():
            sourceCode += '{0}keywords="{1}",{2}'.format(
                istring, self.keywordsEdit.text(), os.linesep)
        
        sourceCode += '{0}packages=find_packages('.format(istring)
        src = Utilities.fromNativeSeparators(
            self.sourceDirectoryPicker.text())
        excludePatterns = []
        for row in range(self.excludePatternList.count()):
            excludePatterns.append(
                self.excludePatternList.item(row).text())
        if src:
            sourceCode += '{0}{1}"{2}"'.format(os.linesep, i1string, src)
            if excludePatterns:
                sourceCode += ','
            else:
                sourceCode += '{0}{1}'.format(os.linesep, istring)
        if excludePatterns:
            sourceCode += '{0}{1}exclude=[{0}'.format(os.linesep, i1string)
            sourceCode += '{0}"{1}"{2}'.format(
                i2string,
                '",{0}{1}"'.format(os.linesep, i2string)
                .join(excludePatterns),
                os.linesep)
            sourceCode += '{0}]{1}{2}'.format(i1string, os.linesep, istring)
        sourceCode += '),{0}'.format(os.linesep)
        
        if self.includePackageDataCheckBox.isChecked():
            sourceCode += '{0}include_package_data = True,{1}'.format(
                istring, os.linesep)
        
        modules = []
        for row in range(self.modulesList.count()):
            modules.append(self.modulesList.item(row).text())
        if modules:
            sourceCode += '{0}py_modules=[{1}'.format(istring, os.linesep)
            sourceCode += '{0}"{1}"{2}'.format(
                i1string,
                '",{0}{1}"'.format(os.linesep, i1string).join(modules),
                os.linesep)
            sourceCode += '{0}],{1}'.format(istring, os.linesep)
        del modules
        
        scripts = []
        for row in range(self.scriptsList.count()):
            scripts.append(self.scriptsList.item(row).text())
        if scripts:
            sourceCode += '{0}scripts=[{1}'.format(istring, os.linesep)
            sourceCode += '{0}"{1}"{2}'.format(
                i1string,
                '",{0}{1}"'.format(os.linesep, i1string).join(scripts),
                os.linesep)
            sourceCode += '{0}],{1}'.format(istring, os.linesep)
        del scripts
        
        sourceCode += "){0}".format(estring)
        return sourceCode
    
    @pyqtSlot()
    def on_projectButton_clicked(self):
        """
        Private slot to populate some fields with data retrieved from the
        current project.
        """
        project = ericApp().getObject("Project")
        
        self.nameEdit.setText(project.getProjectName())
        try:
            self.versionEdit.setText(project.getProjectVersion())
            self.authorEdit.setText(project.getProjectAuthor())
            self.authorEmailEdit.setText(project.getProjectAuthorEmail())
            description = project.getProjectDescription()
        except AttributeError:
            self.versionEdit.setText(project.pdata["VERSION"][0])
            self.authorEdit.setText(project.pdata["AUTHOR"][0])
            self.authorEmailEdit.setText(project.pdata["EMAIL"][0])
            description = project.pdata["DESCRIPTION"][0]
        
        summary = (
            description.split(".", 1)[0].replace("\r", "").replace("\n", "") +
            "."
        )
        self.summaryEdit.setText(summary)
        self.descriptionEdit.setPlainText(description)
        
        self.packageRootPicker.setText(project.getProjectPath())
        
        # prevent overwriting of entries by disabling the button
        self.projectButton.setEnabled(False)
    
    def __getStartDir(self):
        """
        Private method to get the start directory for selection dialogs.
        
        @return start directory
        @rtype str
        """
        return (Preferences.getMultiProject("Workspace") or
                Utilities.getHomeDir())
    
    @pyqtSlot()
    def on_scriptsList_itemSelectionChanged(self):
        """
        Private slot to handle a change of selected items of the
        scripts list.
        """
        self.deleteScriptButton.setEnabled(
            len(self.scriptsList.selectedItems()) > 0)
    
    @pyqtSlot()
    def on_deleteScriptButton_clicked(self):
        """
        Private slot to delete the selected script items.
        """
        for itm in self.scriptsList.selectedItems():
            self.scriptsList.takeItem(
                self.scriptsList.row(itm))
            del itm
    
    @pyqtSlot()
    def on_addScriptButton_clicked(self):
        """
        Private slot to add scripts to the list.
        """
        startDir = self.packageRootPicker.text() or self.__getStartDir()
        scriptsList = EricFileDialog.getOpenFileNames(
            self,
            self.tr("Add Scripts"),
            startDir,
            self.tr("Python Files (*.py);;All Files(*)"))
        for script in scriptsList:
            script = script.replace(
                Utilities.toNativeSeparators(startDir), "")
            if script.startswith(("\\", "/")):
                script = script[1:]
            if script:
                QListWidgetItem(Utilities.fromNativeSeparators(script),
                                self.scriptsList)
    
    @pyqtSlot()
    def on_modulesList_itemSelectionChanged(self):
        """
        Private slot to handle a change of selected items of the
        modules list.
        """
        self.deleteModuleButton.setEnabled(
            len(self.modulesList.selectedItems()) > 0)
    
    @pyqtSlot()
    def on_deleteModuleButton_clicked(self):
        """
        Private slot to delete the selected script items.
        """
        for itm in self.modulesList.selectedItems():
            self.modulesList.takeItem(
                self.modulesList.row(itm))
            del itm
    
    @pyqtSlot()
    def on_addModuleButton_clicked(self):
        """
        Private slot to add Python modules to the list.
        """
        startDir = self.packageRootPicker.text() or self.__getStartDir()
        modulesList = EricFileDialog.getOpenFileNames(
            self,
            self.tr("Add Python Modules"),
            startDir,
            self.tr("Python Files (*.py)"))
        for module in modulesList:
            module = module.replace(
                Utilities.toNativeSeparators(startDir), "")
            if module.startswith(("\\", "/")):
                module = module[1:]
            if module:
                QListWidgetItem(os.path.splitext(module)[0]
                                .replace("\\", ".").replace("/", "."),
                                self.modulesList)
    
    @pyqtSlot()
    def on_excludePatternList_itemSelectionChanged(self):
        """
        Private slot to handle a change of selected items of the
        exclude pattern list.
        """
        self.deleteExcludePatternButton.setEnabled(
            len(self.excludePatternList.selectedItems()) > 0)
    
    @pyqtSlot()
    def on_deleteExcludePatternButton_clicked(self):
        """
        Private slot to delete the selected exclude pattern items.
        """
        for itm in self.excludePatternList.selectedItems():
            self.excludePatternList.takeItem(
                self.excludePatternList.row(itm))
            del itm
    
    @pyqtSlot()
    def on_addExludePatternButton_clicked(self):
        """
        Private slot to add an exclude pattern to the list.
        """
        pattern = (
            self.excludePatternEdit.text().replace("\\", ".").replace("/", ".")
        )
        if not self.excludePatternList.findItems(
            pattern,
            Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchCaseSensitive
        ):
            QListWidgetItem(pattern, self.excludePatternList)
    
    @pyqtSlot(str)
    def on_excludePatternEdit_textChanged(self, txt):
        """
        Private slot to handle a change of the exclude pattern text.
        
        @param txt text of the line edit
        @type str
        """
        self.addExludePatternButton.setEnabled(bool(txt))
    
    @pyqtSlot()
    def on_excludePatternEdit_returnPressed(self):
        """
        Private slot handling a press of the return button of the
        exclude pattern edit.
        """
        self.on_addExludePatternButton_clicked()
