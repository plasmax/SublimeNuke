﻿from pprint import pprint
import types

from PySide import QtGui, QtCore, QtOpenGL

class VisualDebug(QtGui.QWidget):
    """
    A TreeView containing downwards recursively searched 
    QObjects through their 'children' attribute. On object selection,
    additional information is displayed in separate widgets:
    QMetaMethod and QMetaPropety info in separate QListViews
    Layout count QListView
    Web scraped QT 4.8 Class information
    """
    def __init__(self):
        super(VisualDebug, self).__init__()
        self.layout = QtGui.QGridLayout(self)

        self.setMinimumWidth(900)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.treeview = WidgetTreeView()
        self.treemodel = QtGui.QStandardItemModel()
        self.treeview.setModel(self.treemodel)
        self.treeview.setUniformRowHeights(True)

        self.layout.addWidget(self.treeview)
        self.treemodel.setHorizontalHeaderLabels(['metaObject className', 
                                                'objectName',
                                                'windowTitle', 
                                                'text', 
                                                'title', 
                                                '__repr__',
                                                'python object'])

        self.treeview.header().setStretchLastSection(False)
        self.treeview.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        rootItem = self.treemodel.invisibleRootItem()
        for w in QtGui.qApp.topLevelWidgets(): #extra stuff
            self.recurseWidgets(w, rootItem)

    def getObjectInfo( self, widget, indent=0 ):
        return [widget.metaObject().className(), 
                        widget.objectName(),
                        (widget.windowTitle() if hasattr(widget, 'windowTitle') else '' ),
                        (widget.text() if hasattr(widget, 'text') else '' ),
                        (widget.title() if hasattr(widget, 'title') else '' ),
                        (widget.windowTitle() if hasattr(widget, 'windowTitle') else '' ),
                        widget.__repr__()]

    def recurseWidgets( self, widget , parent):
        # later try and turn this into a generator pushed by a Qtimer
        # treeInfo = {}
        def recursion(widget, parent):
            for child in widget.children():
                infoList = self.getObjectInfo(child)
                items = [ QtGui.QStandardItem(info) for info in infoList ] 
                parent.appendRow(items)
                childItem = items[0]
                childItem.setData(child, QtCore.Qt.UserRole)
                # childItem = QtGui.QStandardItem(', '.join(info))
                recursion(child, childItem)

        infoList = self.getObjectInfo(widget)
        items = [ QtGui.QStandardItem(info) for info in infoList ] 
        # parentItem = QtGui.QStandardItem(', '.join(info)) #later setData adding widget object
        parent.appendRow(items)
        firstParent = items[0]
        firstParent.setData(widget, QtCore.Qt.UserRole)
        # parent.appendRow(parentItem)
        recursion(widget, firstParent)
        # return treeInfo

class WidgetTreeView(QtGui.QTreeView):
    def mousePressEvent(self, event):

        self.selectedIndices = self.selectedIndexes()
        if bool(self.selectedIndices):
            self.widget = self.model().data(self.selectedIndices[0], QtCore.Qt.UserRole)
            print self.widget

        if event.button() == QtCore.Qt.RightButton:
            self.menu = QtGui.QMenu()

            self.regularMenu = QtGui.QMenu('regular')
            self.menu.addMenu(self.regularMenu)

            self.builtInMethodMenu = QtGui.QMenu('built-in methods')
            self.regularMenu.addMenu(self.builtInMethodMenu)

            self.eventMenu = QtGui.QMenu('events')
            self.builtInMethodMenu.addMenu(self.eventMenu)

            self.methodMenu = QtGui.QMenu('method-wrappers')
            self.regularMenu.addMenu(self.methodMenu)

            self.dictMenu = QtGui.QMenu('dict types')
            self.regularMenu.addMenu(self.dictMenu)

            for method in dir(self.widget):

                attr = getattr(self.widget, method)

                if isinstance(attr, types.BuiltinMethodType):
                    if 'event' in method.lower():
                        self.eventMenu.addAction(method, 
                            lambda method=attr, 
                            widget=self.widget: self.testWidget(method, widget))
                    else:
                        self.builtInMethodMenu.addAction(method,
                            lambda method=attr, 
                            widget=self.widget: self.testWidget(method, widget)) 

                elif isinstance(attr, type(self.widget.__init__)):
                    self.methodMenu.addAction(method,
                        lambda method=attr, widget=self.widget: self.testWidget(method, widget)) 

                elif isinstance(attr, types.DictType):
                    for key in attr.keys():
                        try:
                            value = attr.get(key)
                            print attr, value
                            self.dictMenu.addAction(', '.join([key, str(value)]), self.dud)
                        except:
                            pass

                elif isinstance(attr, QtGui.QPaintDevice.PaintDeviceMetric):
                    pass #seems boring

                else:
                    try:
                         self.regularMenu.addAction(', '.join([method,str(attr), str(type(attr))]), 
                            lambda method=attr, widget=self.widget: self.testWidget(method, widget))
                    except:
                        pass

            self.metaMenu = QtGui.QMenu('meta')
            self.menu.addMenu(self.metaMenu)

            self.metaMethodMenu = QtGui.QMenu('meta methods')
            self.metaMenu.addMenu(self.metaMethodMenu)
            
            o = self.widget
            conn = QtCore.Qt.QueuedConnection
            for method, signature in self.getMetaMethods(self.widget):

                self.metaMethodMenu.addAction(signature, 
                    lambda obj=o, conn=conn: o.metaObject().invokeMethod(obj,
                    QtCore.QGenericArgument()))

            self.metaPropMenu = QtGui.QMenu('meta properties')
            self.metaMenu.addMenu(self.metaPropMenu)

            for name, prop in self.getMetaProperties(self.widget):
                self.metaPropMenu.addAction(name, 
                    lambda obj=o: prop.read(o))

            self.menu.exec_(QtGui.QCursor().pos())

        else:
            super(self.__class__, self).mousePressEvent(event)

    def testWidget(self, method, widget):
        print method.__call__()

    def dud(self):
        pass

    def getMetaMethods(self, obj):
        methods = []
        m = obj.metaObject()
        for i in range(m.methodOffset(),m.methodCount()):
            metaMethod = m.method(i)
            signature = metaMethod.signature()
            methods.append((metaMethod, signature))
        return methods

    def getMetaProperties(self, obj):
        properties = []
        m = obj.metaObject()
        for i in range(m.propertyOffset(),m.propertyCount()):
            metaproperty = m.property(i)
            name = metaproperty.name()
            properties.append((name, metaproperty))
        return properties

for w in QtGui.qApp.topLevelWidgets():
    if w.metaObject().className() == 'VisualDebug':
        print w
        w.deleteLater()
        
vdb = VisualDebug()
vdb.show()


@QtCore.Slot(object)
def shabam(*args, **kwargs):
    print args, kwargs, 'SHABAM!'

vdb.destroyed.connect(shabam)
# vdb.deleteLater()

def getObjectInfo(widget, indent=0):
    objectInfo = {}
    if hasattr(widget, 'objectName') and widget.objectName() != '':
        objectInfo['objectName'] = widget.objectName()
    if hasattr(widget, 'metaObject') and widget.metaObject() != '':
        objectInfo['metaObject'] = widget.metaObject().className()
    if hasattr(widget, 'windowTitle') and widget.windowTitle() != '':
        objectInfo['windowTitle'] = widget.windowTitle()
    return objectInfo

def recurseWidgets( widget ):
    treeInfo = {}
    def recursion(widget, indents):
        indents += 1
        childDict = {}
        for child in widget.children():
            childDict[widget.__repr__()] = getObjectInfo(child, indent=indents)
            recursion(child, indents)
        treeInfo[widget.__repr__()] = childDict
    indents = 1
    treeInfo[widget.__repr__()] = getObjectInfo(widget, indent=indents)
    recursion(widget, indents)
    return treeInfo
