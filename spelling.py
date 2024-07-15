# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Spelling
                                 A QGIS plugin
 Check the spelling of words in Print Layout elements
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin           : 2024-07-15
        git sha         : $Format:%H$
        copyright       : (C) 2024 by Ian Turton, GDSG, University of Glasgow
        email           : ian@ianturton.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

# Initialize Qt resources from file resources.py
# from .resources import
# Import the code for the dialog
import os.path
from pathlib import Path
from .spelling_dialog import SpellingDialog


from qgis.utils import plugins
from qgis.core import check, QgsAbstractValidityCheck, QgsValidityCheckResult
from qgis.core import QgsLayoutItemLabel
import string
from spellchecker import SpellChecker


class Spelling:
    """QGIS Plugin Implementation."""

    checker = SpellChecker()

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Spelling_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Spell Checker')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Spelling', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/spelling/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'spelling'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Spell Checker'),
                action)
            self.iface.removeToolBarIcon(action)

    def select_output_file(self):
        filename, _ = QFileDialog.getSaveFileName(self.dlg, "Select dictionary file ", "", '*.txt')
        if filename:
            self.dlg.lineEdit.setText(filename)

    def run(self):
        """Run method that performs all the real work"""
        # TODO - work out how to construct this from the list returned by SpellChecker.languages
        langs = {'English': 'en',
                 'Spanish': 'es',
                 'French': 'fr',
                 'Portuguese': 'pt',
                 'German': 'de',
                 'Italian': 'it',
                 'Russian': 'ru',
                 'Arabic': 'ar',
                 'Basque': 'eu',
                 'Latvian': 'lv',
                 'Dutch': 'nl'
                 }
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg = SpellingDialog()
            self.dlg.comboBox.addItems(langs.keys())
            self.dlg.lineEdit.clear()
            self.dlg.pushButton.clicked.connect(self.select_output_file)
            self.create_checker('en')
            # TODO look up local language and select that if it exists

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            idx = self.dlg.comboBox.currentText()
            self.create_checker(langs[idx])

    def create_checker(self, language):
        self.checker = SpellChecker(language=language)
        if self.dlg.lineEdit.text():
            dictionary = Path(self.dlg.lineEdit.text())
        else:
            dictionary = Path(Path(self.iface.userProfileManager().userProfile().folder()),
                              'spelling.txt')
        if not dictionary.exists():
            open(dictionary, 'w').close()

        self.checker.word_frequency.load_text_file(dictionary)


@check.register(type=QgsAbstractValidityCheck.TypeLayoutCheck)
def layout_check_spelling(context, feedback):
    _instance = plugins['qgis-spellcheck']
    checker = _instance.checker

    layout = context.layout
    results = []
    if not checker:
        checker = SpellChecker()

    for i in layout.items():
        if isinstance(i, QgsLayoutItemLabel):
            text = i.currentText()
            tokens = [word.strip(string.punctuation) for word in text.split()]
            misspelled = checker.unknown(tokens)
            for word in misspelled:
                res = QgsValidityCheckResult()
                res.type = QgsValidityCheckResult.Warning
                res.title = 'Spelling Error?'
                template = f"""
                <strong>'{word}</strong>' may be misspelled, would
                '<strong>{checker.correction(word)}</strong>' be a better choice?
                """
                possibles = checker.candidates(word)
                if len(possibles) > 1:
                    template += """
                    Or one of:<br/>
                    <ul>

                    """
                    for t in possibles:
                        template += f"<li>{t}</li>\n"

                    template += '</ul>'
                res.detailedDescription = template
                results.append(res)

    return results
