from PythonEditor.ui.Qt import QtWidgets, QtCore
from PythonEditor.ui import terminal
from PythonEditor.ui import tabs
from PythonEditor.ui import menubar
from PythonEditor.ui.features import shortcuts
from PythonEditor.ui.features import actions
from PythonEditor.ui.features import autosavexml
from PythonEditor.ui.dialogs import preferences
from PythonEditor.ui.dialogs import shortcuteditor


class PythonEditor(QtWidgets.QWidget):
    """
    Main widget. Sets up layout
    and connects some signals.
    """
    def __init__(self, parent=None):
        super(
            PythonEditor,
            self
        ).__init__(parent=parent)
        self.setObjectName('PythonEditor')
        self._parent = parent
        if parent is not None:
            self.setParent(parent)

        self.construct_ui()

    def construct_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setObjectName(
            'PythonEditor_MainLayout'
        )
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabeditor = tabs.TabEditor(self)
        self.editor = self.tabeditor.editor
        self.terminal = terminal.Terminal()

        splitter = QtWidgets.QSplitter(
            QtCore.Qt.Vertical
        )
        splitter.setObjectName(
            'PythonEditor_MainVerticalSplitter'
        )
        splitter.addWidget(self.terminal)
        splitter.addWidget(self.tabeditor)

        layout.addWidget(splitter)

        act = actions.Actions(
            editor=self.editor,
            tabeditor=self.tabeditor,
            terminal=self.terminal,
            use_tabs=True
        )

        sch = shortcuts.ShortcutHandler(
			self.tabeditor,
			use_tabs=True
		)
        sch.clear_output_signal.connect(self.terminal.clear)

        self.menubar = menubar.MenuBar(self)

        SE = shortcuteditor.ShortcutEditor
        self.shortcuteditor = SE(sch)

        PE = preferences.PreferencesEditor
        self.preferenceseditor = PE()

		# Loading the AutosaveManager will also load
        # all the contents of the autosave into tabs.
        AM = autosavexml.AutoSaveManager
        self.filehandler = AM(
            self.tabeditor
        )
