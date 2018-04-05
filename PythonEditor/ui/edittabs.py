from Qt import QtWidgets, QtCore
from editor import Editor

class EditTabs(QtWidgets.QTabWidget):
    """
    QTabWidget containing Editor
    QPlainTextEdit widgets.
    """
    widget_changed_signal = QtCore.Signal(object)

    def __init__(self):
        QtWidgets.QTabWidget.__init__(self)
        self.setTabsClosable(True)
        self.new_tab()
        self._build_tabs()
        self.currentChanged.connect(self.widgetChanged)
        self.tabCloseRequested.connect(self.close_tab)

    def _build_tabs(self):
        self.insertTab(1, QtWidgets.QWidget(),'')
        nb = self.new_btn = QtWidgets.QToolButton()
        nb.setObjectName('Tab_Widget_New_Button')
        nb.setMinimumSize(QtCore.QSize(50,10))
        nb.setText('+') # you could set an icon instead of text
        nb.setAutoRaise(True)
        nb.clicked.connect(self.new_tab)
        self.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, nb)
        self.tabBar().setTabEnabled(1, False)

    @QtCore.Slot(str)
    def new_tab(self):
        index = self.count() - 1
        editor = Editor(handle_shortcuts=False)
        self.insertTab(index, 
                       editor, 
                       'New Tab')
        self.setCurrentIndex(index)

    def close_current_tab(self):
        """
        TODO: 
        1) Block/return if tab is '+' tab.
        2) Maybe check to see if file contents is saved 
        somewhere. Restore all tabs on open from xml <subscript> ?
        """
        _index = self.currentIndex()
        self.close_tab(_index)

    def close_tab(self, index):
        _index = self.currentIndex()

        old_widget = self.widget(index)
        if old_widget.objectName() != 'Editor':
            return
        old_widget.deleteLater()

        self.removeTab(index)
        index = self.count() - 1
        self.setCurrentIndex(_index-1)

    @QtCore.Slot(int)
    def widgetChanged(self, index):
        """
        Triggers widget_changed signal
        with current widget.
        """
        self.widget_changed_signal.emit(self.currentWidget())
