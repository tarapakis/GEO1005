# -*- coding: utf-8 -*-
"""
/***************************************************************************
 escapersDockWidget
                                 A QGIS plugin
 where are the animals
                             -------------------
        begin                : 2017-12-15
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Teng_Takis_Giorgos
        email                : tengwu95@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import os.path
import random
import csv
import time

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Initialize Qt resources from file resources.py
import resources

from PyQt4 import QtGui,QtCore, uic
from PyQt4.QtCore import pyqtSignal,QVariant
from qgis.core import *
from qgis.networkanalysis import *
from qgis.gui import *
import processing
import qgis
from . import utility_functions as uf

from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsFeature, QgsGeometry



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'escapers_dockwidget_base.ui'))




class escapersDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    flag = 0

    def __init__(self,iface, parent=None):
        """Constructor."""
        super(escapersDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.iface = iface
        self.canvas = self.iface.mapCanvas()

        self.iface.projectRead.connect(self.updateLayers)
        self.iface.newProjectCreated.connect(self.updateLayers)
        self.iface.legendInterface().itemRemoved.connect(self.updateLayers)
        self.iface.legendInterface().itemAdded.connect(self.updateLayers)

        self.OpenScenarioButton.clicked.connect(self.OpenScenario)
        self.SaveScenarioButton.clicked.connect(self.SaveScenario)

        #Selectlayer
        self.selectLayerCombo.activated.connect(self.setSelectedLayer)
        #self.selectAttributeCombo.activated.connect(self.setSelectedAttribute)

        self.bufferButton.clicked.connect(self.calculateBuffer)
        self.addpointbutton.clicked.connect(self.addPoint)
        self.intersectionbutton.clicked.connect(self.intersection)
        self.cleanButton.clicked.connect(self.cleanBuffer)
        self.updatePlaceButton.clicked.connect(self.updatePlace)
        self.openTableButton.clicked.connect(self.opentable)


        self.emitPoint = QgsMapToolEmitPoint(self.canvas)
        self.emitPoint.canvasClicked.connect(self.getPoint)



        #self.updateLayers()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


    def CreateBuffer(self):
        layer = self.canvas.layer(0);


    def OpenScenario(self, filename=""):
        scenario_open = False
        scenario_file = os.path.join(u'/Users/tengw/github/GEO1005', 'sample_data', 'time_test.qgs')
            # check if file exists
        if os.path.isfile(scenario_file):
            self.iface.addProject(scenario_file)
            scenario_open = True
        else:
            last_dir = uf.getLastDir("SDSS")
            new_file = QtGui.QFileDialog.getOpenFileName(self, "", last_dir, "(*.qgs)")
            if new_file:
                self.iface.addProject(unicode(new_file))
                scenario_open = True
        if scenario_open:
            self.updateLayers()

    def SaveScenario(self):
        self.iface.actionSaveProject()

    def updateLayers(self):
        layers = uf.getLegendLayers(self.iface, 'all', 'all')
        self.selectLayerCombo.clear()
        if layers:
            layer_names = uf.getLayersListNames(layers)
            self.selectLayerCombo.addItems(layer_names)
            self.setSelectedLayer()


    def setSelectedLayer(self):
        pass

    def getSelectedLayer(self):
        layer_name = self.selectLayerCombo.currentText()
        layer = uf.getLegendLayerByName(self.iface, layer_name)
        return layer



    def setSelectedAttribute(self):
        field_name = self.selectAttributeCombo.currentText()
        self.updateAttribute.emit(field_name)

    def getSelectedAttribute(self):
        field_name = self.selectAttributeCombo.currentText()
        return field_name




# buffer functions
    def getspeed(self):
        speed = self.speedEdit.text()
        if uf.isNumeric(speed):
            return uf.convertNumeric(speed)
        else:
            return 0

    def gettime(self):
        time = self.timeEdit.text()
        if uf.isNumeric(time):
            return uf.convertNumeric(time)
        else:
            return 0

    def getBufferCutoff(self):
        cutoff = self.bufferCutoffEdit.text()
        if uf.isNumeric(cutoff):
            return uf.convertNumeric(cutoff)
        else:
            return 0

    def calculateBuffer(self):
        #distance = self.getBufferCutoff()
        distance = self.getspeed()* self.gettime()
        layer = self.getSelectedLayer()
        processing.runandload("qgis:fixeddistancebuffer", layer, distance, 35, False, None)

    def refreshCanvas(self, layer):
        if self.canvas.isCachingEnabled():
            layer.setCacheImage(None)
        else:
            self.canvas.refresh()

    def getlayer1(self):
        layer1 = self.layer1Edit.text()
        return  layer1
    def getlayer2(self):
        layer2 = self.layer2Edit.text()
        return  layer2
    def intersection(self):
        layer1 = self.getlayer1()
        layer2 = self.getlayer2()
        processing.runandload('qgis:intersection',layer1, layer2, None, 'memory:output')

    def addPoint(self):
        self.flag = 1
        place = uf.getLegendLayerByName(self.iface, 'escape place')
        if not place:
            attribs = ["id"]    #[a,b,c]
            types = [QVariant.String]    #[a,b,c]

            place = QgsVectorLayer('Point?crs=epsg:28992', 'place', 'memory')
            uf.addFields(place, ['id'], [QVariant.String])
            uf.loadTempLayer(place)
            place.setLayerName('escape place')

        place.startEditing()
        self.userTool = self.canvas.mapTool()
        self.canvas.setMapTool(self.emitPoint)
        self.refreshCanvas(place)

    def getPoint(self,mapPoint):
        self.canvas.unsetMapTool(self.emitPoint)
        self.canvas.setMapTool(self.userTool)
        if self.flag == 1:
            place = uf.getLegendLayerByName(self.iface, 'escape place')#get layer named"escape place"
        else:
            place = uf.getLegendLayerByName(self.iface, 'new place')
        if mapPoint:
            pr = place.dataProvider()
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPoint(mapPoint))
            pr.addFeatures([feature])
            place.commitChanges()#savechanges


    def refreshCanvas(self, layer):
        # refresh canvas after changes
        if self.canvas.isCachingEnabled():
            layer.setCacheImage(None)
        else:
            self.canvas.refresh()

    def cleanBuffer(self):
        layer = uf.getLegendLayerByName(self.iface, 'Buffer')
        if layer:
            QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

    def updatePlace(self):
        self.flag = 0
        place = uf.getLegendLayerByName(self.iface, 'new place')
        if not place:
            attribs = ["id"]  # [a,b,c]
            types = [QVariant.String]  # [a,b,c]

            place = QgsVectorLayer('Point?crs=epsg:28992', 'place', 'memory')
            uf.addFields(place, ['id'], [QVariant.String])
            uf.loadTempLayer(place)
            place.setLayerName('new place')

        place.startEditing()
        self.userTool = self.canvas.mapTool()
        self.canvas.setMapTool(self.emitPoint)
        self.refreshCanvas(place)

    def extractAttributeSummary(self):
        # get summary of the attribute
        #layer = self.getSelectedLayer()
        layer = uf.getLegendLayerByName(self.iface, 'animaldt')#get layer named"escape place"
        summary = []
        # only use the first attribute in the list
        for feature in layer.getFeatures():
            summary.append((feature.attributes()[0], feature.attributes()[2],feature.attributes()[5]))
        # send this to the table
        self.clearTable()
        self.updateTable(summary)

    def updateTable(self, values):
        # takes a list of label / value pairs, can be tuples or lists. not dictionaries to control order
        self.statisticsTable.setColumnCount(2)
        self.statisticsTable.setHorizontalHeaderLabels(["Item", "Value"])
        self.statisticsTable.setRowCount(len(values))
        for i, item in enumerate(values):
            # i is the table row, items must tbe added as QTableWidgetItems
            self.statisticsTable.setItem(i, 0, QtGui.QTableWidgetItem(unicode(item[0])))
            self.statisticsTable.setItem(i, 1, QtGui.QTableWidgetItem(unicode(item[1])))
            self.statisticsTable.setItem(i, 1, QtGui.QTableWidgetItem(unicode(item[2])))
        self.statisticsTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.statisticsTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.statisticsTable.resizeRowsToContents()

    def clearTable(self):
        self.statisticsTable.clear()





