# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name            : geoTOPSIS
Description     : geographical MCDA 
Date            : June 27, 2014
copyright		: (C) 2018 by Gianluca Massei
email			: (g_massa@libero.it)

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog,QMessageBox, QTableWidget, QTableWidgetItem, QMenu
from qgis.PyQt import QtGui
from qgis.core import *
from qgis.gui import *
	
import os
import webbrowser
import shutil
import csv

try:
	import numpy as np
except ImportError as e:
	QMessageBox.information(None, QCoreApplication.translate('geoTOPSIS', "Plugin error"), \
	QCoreApplication.translate('geoTOPSIS', "Couldn't import Python module. [Message: %s]" % e))
	


#import DOMLEM
from . import htmlGraph

from .ui_geoTOPSIS import Ui_Dialog

class geoTOPSISDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())
		self.setupUi(self)
		self.iface = iface
		self.activeLayer = self.iface.activeLayer()
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,False)
		#QObject.connect(self.SetBtnQuit, SIGNAL("clicked()"),self, SLOT("reject()"))
		self.SetBtnQuit.clicked.connect(self.reject)
		self.SetBtnAbout.clicked.connect(self.about)
		self.AnlsSetBtnAbout.clicked.connect(self.about)
		self.SetBtnHelp.clicked.connect(self.open_help)
		#QObject.connect(self.EnvAddFieldBtn, SIGNAL( "clicked()" ), self.AddField)	
		self.EnvCalculateBtn.clicked.connect(self.AnalyticHierarchyProcess)
		self.EnvGetWeightBtn.clicked.connect(self.Elaborate)
		self.RenderBtn.clicked.connect(self.RenderLayer)
		self.GraphBtn.clicked.connect(self.BuildOutput)
		#QObject.connect(self.AnlsBtnBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		self.AnlsBtnBox.clicked.connect(self.reject)
		
		sourceIn=str(self.iface.activeLayer().source())
		pathSource=os.path.dirname(sourceIn)
		outputFile="geoTOPSIS.shp"
		sourceOut=os.path.join(pathSource,outputFile)
		#self.OutlEdt.setText(str(sourceOut))
		self.EnvMapNameLbl.setText(self.activeLayer.name())
		self.EnvlistFieldsCBox.addItems(self.GetFieldNames(self.activeLayer))
		self.LabelListFieldsCBox.addItems([str(f.name()) for f in self.activeLayer.fields()])
#################################################################################
		Envfields=self.GetFieldNames(self.activeLayer) #field list
		self.EnvTableWidget.setColumnCount(len(Envfields))
		self.EnvTableWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvTableWidget.setRowCount(len(Envfields))
		self.EnvTableWidget.setVerticalHeaderLabels(Envfields)
		EnvSetLabel=["Weigths","Preference","Ideal point", "Worst point "]
		self.EnvParameterWidget.setColumnCount(len(Envfields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvParameterWidget.setRowCount(4)
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)
		for r in range(len(Envfields)):
			self.EnvTableWidget.setItem(r,r,QTableWidgetItem("1.0"))
		self.EnvTableWidget.cellChanged[(int,int)].connect(self.CompleteMatrix)
		self.updateTable()
		try:
			self.EnvParameterWidget.cellClicked[(int,int)].connect(self.ChangeValue)
		except:
			pass
###############################ContextMenu########################################
		headers = self.EnvParameterWidget.horizontalHeader()
		headers.setContextMenuPolicy(Qt.CustomContextMenu)
		headers.customContextMenuRequested.connect(self.popMenu)
#################################################################################
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,True)
			
		setting=self.csv2setting()
		try:
			self.setting2table(setting)
		except:
			pass

	def GetFieldNames(self, layer):
		"""retrive field names from active map/layer"""
		fields = layer.dataProvider().fields()
		fieldList=[f.name() for f in fields if f.typeName()!='String']
		return fieldList # sorted( field_list, cmp=locale.strcoll )



	def outFile(self):
		"""Display file dialog for output  file"""
		self.OutlEdt.clear()
		outvLayer, __ = QFileDialog.getSaveFileName(self, "Output map",".", "ESRI Shapefile (*.shp)")
		self.OutlEdt.insert(outvLayer)
		return outvLayer
		
		
	def updateTable(self):
		"""Prepare and compile table in GUI"""
		fields=self.GetFieldNames(self.activeLayer)
		#fields = [field.name() for field in self.activeLayer.pendingFields() ]
		pathSource=os.path.dirname(str(self.activeLayer.source()))
		self.EnvTableWidget.setColumnCount(len(fields))
		self.EnvTableWidget.setHorizontalHeaderLabels(fields)
		self.EnvTableWidget.setRowCount(len(fields))
		self.EnvTableWidget.setVerticalHeaderLabels(fields)
		EnvSetLabel=["Weigths","Preference","Ideal point", "Worst point "]
		self.EnvParameterWidget.setColumnCount(len(fields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(fields)
		self.EnvParameterWidget.setRowCount(4)
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)
		for r in range(len(fields)):
			self.EnvParameterWidget.setItem(0,r,QTableWidgetItem("1.0"))
			self.EnvParameterWidget.setItem(1,r,QTableWidgetItem("gain"))
		self.updateGUIIdealPoint()
		return 0


	def updateGUIIdealPointFctn(self,TableWidget,WeighTableWidget,provider):
		"""base function for updateGUIIdealPoint()"""
		criteria=[TableWidget.verticalHeaderItem(f).text() for f in range(TableWidget.columnCount())]
		preference=[str(WeighTableWidget.item(1, c).text()) for c in range(WeighTableWidget.columnCount())]
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		minField=[provider.minimumValue( f ) for f in fids]
		maxField=[provider.maximumValue( f ) for f in fids]
		for r in range(len(preference)):
			if preference[r]=='gain':
				WeighTableWidget.setItem(2,r,QTableWidgetItem(str(maxField[r])))#ideal point
				WeighTableWidget.setItem(3,r,QTableWidgetItem(str(minField[r])))#worst point
			elif preference[r]=='cost':
				WeighTableWidget.setItem(2,r,QTableWidgetItem(str(minField[r])))
				WeighTableWidget.setItem(3,r,QTableWidgetItem(str(maxField[r])))
			else:
				WeighTableWidget.setItem(2,r,QTableWidgetItem("0"))
				WeighTableWidget.setItem(3,r,QTableWidgetItem("0"))
	
	def updateGUIIdealPoint(self):
		provider=self.activeLayer.dataProvider() #provider=self.active_layer.dataProvider() 
		##Environmental
		self.updateGUIIdealPointFctn(self.EnvTableWidget,self.EnvParameterWidget,provider)
		return 0


	def popMenu(self,pos):
		fields=list(range(10))
		menu = QMenu()
		removeAction = menu.addAction("Remove selected fields")
		reloadAllFields=menu.addAction("Add deleted fields")
		action = menu.exec_(self.mapToGlobal(QPoint(pos)))
		if action == removeAction:
			self.removePopup()
		elif action==reloadAllFields:
			self.addPopup()
			

	def removePopup(self):
		selected = sorted(self.EnvParameterWidget.selectionModel().selectedColumns(),reverse=True)
		if len(selected) > 0:
			for s in selected:
				self.removeField(s.column())
			self.EnvParameterWidget.setCurrentCell(-1,-1)
		else:
			QMessageBox.warning(self.iface.mainWindow(), "geoWeightedSum",
			("column must to be selected"), QMessageBox.Ok, QMessageBox.Ok)
		return 0
		
		
	def addPopup(self):
		Envfields=self.GetFieldNames(self.activeLayer) #field list
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		difference=set(Envfields)-set(criteria)
		for f in difference:
			self.addField(f)
			

	def removeField(self,i):
		"""Remove field in table in GUI"""
		self.EnvTableWidget.removeColumn(i)
		self.EnvTableWidget.removeRow(i)
		self.EnvParameterWidget.removeColumn(i)
		return 0

	def addFieldFctn(self,listFields,TableWidget,WeighTableWidget):
		"""base function for AddField()"""
		TableWidget.insertColumn(TableWidget.columnCount())
		TableWidget.insertRow(TableWidget.rowCount())
		TableWidget.setHorizontalHeaderItem((TableWidget.columnCount()-1),QTableWidgetItem(listFields))
		TableWidget.setVerticalHeaderItem((TableWidget.rowCount()-1),QTableWidgetItem(listFields))
		##############
		WeighTableWidget.insertColumn(WeighTableWidget.columnCount())
		WeighTableWidget.setHorizontalHeaderItem((WeighTableWidget.columnCount()-1),QTableWidgetItem(listFields))
		WeighTableWidget.setItem(0,(WeighTableWidget.columnCount()-1),QTableWidgetItem("1.0"))
		WeighTableWidget.setItem(1,(WeighTableWidget.columnCount()-1),QTableWidgetItem("gain"))
		WeighTableWidget.setItem(2,(WeighTableWidget.columnCount()-1),QTableWidgetItem("0.0"))
		WeighTableWidget.setItem(3,(WeighTableWidget.columnCount()-1),QTableWidgetItem("0.0"))
		return 0
			
	def addField(self,listFields=''):
		"""Add field to table in GUI"""
		if listFields=='':
			listFields=self.EnvlistFieldsCBox.currentText()
		self.addFieldFctn(listFields,self.EnvTableWidget,self.EnvParameterWidget)
		return 0
		

	def CompleteMatrix(self):
		"""Autocomplete matrix of  pairwise comparison"""
		try:
			cell=self.EnvTableWidget.currentItem()
			if cell.text()!=None and type(float(cell.text())==float):
				val=round(float(cell.text())**(-1),2)
				self.EnvTableWidget.setItem(cell.column(),cell.row(),QTableWidgetItem(str(val)))
			return 0
		except ValueError:
			QMessageBox.warning(self.iface.mainWindow(), "geoTOPSYS",
			("Input error\n" "Please insert numeric value "\
			"active"), QMessageBox.Ok, QMessageBox.Ok)


	def ChangeValue(self):
		"""Event for change gain/cost"""
		cell=self.EnvParameterWidget.currentItem()
		r=cell.row()
		c=cell.column()
		first=self.EnvParameterWidget.item(2, c).text()
		second=self.EnvParameterWidget.item(3, c).text()
		if cell.row()==1:
			val=cell.text()
			if val=="cost":
				self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
			elif val=="gain":
				self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
			else:
				self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
			self.EnvParameterWidget.setItem(2,c, QTableWidgetItem(second))
			self.EnvParameterWidget.setItem(3,c, QTableWidgetItem(first))

		
	def csv2setting(self):
		currentDIR = (os.path.dirname(str(self.activeLayer.source())))
		setting=[]
		try:
			with open(os.path.join(currentDIR,'setTOPSIS.csv')) as csvFile:
				csvReader = csv.reader(csvFile, delimiter=";", quotechar='"')
				for row in csvReader:
					setting.append(row)
			return setting
		except:
			QgsMessageLog.logMessage("Problem in reading setting file","geo")

	def setting2table(self,setting):
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		for i in range(len(criteria)):
			for l in range(len(setting[0])):
				if criteria[i]==setting[0][l]:
					self.EnvParameterWidget.setItem(0,i,QTableWidgetItem(str(setting[1][l])))
					self.EnvParameterWidget.setItem(1,i,QTableWidgetItem(str(setting[2][l])))
					self.EnvParameterWidget.setItem(2,i,QTableWidgetItem(str(setting[3][l])))
					self.EnvParameterWidget.setItem(3,i,QTableWidgetItem(str(setting[4][l])))

			
	def Elaborate(self):
		matrix=self.StandardizationIdealPoint()
		self.RelativeCloseness(matrix)
		#self.OveralValue()
		self.setModal(True)
		return 0
#############################################################################################################

	def calculateWeight(self,pairwise):
		"Define vector of weight based on eigenvector and eigenvalues"
		try:
			import numpy as np
			pairwise=np.array(pairwise)
			eigenvalues, eigenvector=np.linalg.eig(pairwise)
			maxindex=np.argmax(eigenvalues)
			eigenvalues=np.float32(eigenvalues)
			eigenvector=np.float32(eigenvector)
			weight=eigenvector[:, maxindex] #extract vector from eigenvector with max vaue in eigenvalues
			weight.tolist() #convert array(numpy)  to vector
			weight=[ w/sum(weight) for w in weight ]
			for i in range(len(weight)):
				self.EnvParameterWidget.setItem(0,i,QTableWidgetItem(str(round(weight[i],2))))
			return weight, eigenvalues, eigenvector
		except ImportError as e:
			QMessageBox.information(None, QCoreApplication.translate('geoTOPSYS', "Plugin error"), \
			QCoreApplication.translate('geoTOPSYS', "Couldn't import Python module 'numpy'.  You can install 'numpy' \
			with the following command: sudo easy_install numpy'.<br> or you can use 32bit version of QGS. [Message: %s]" % e))
			return

	def Consistency(self,weight,eigenvalues):
		"Calculete Consistency index in accord with Saaty (1977)"
		try:
			RI=[0.00, 0.00, 0.00,0.52,0.90,1.12,1.24,1.32,1.41]     #order of matrix: 0,1,2,3,4,5,6,7,8
			order=len(weight)
			CI=(np.max(eigenvalues)-order)/(order-1)
			return CI/RI[order-1]
		except:
			return 1.41

	def AnalyticHierarchyProcess(self):
		"""Calculate weight from matrix of pairwise comparison """
			
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		pairwise=[[float(self.EnvTableWidget.item(r, c).text()) for r in range(len(criteria))] for c in range(len(criteria))]
		weight, eigenvalues, eigenvector=self.calculateWeight(pairwise)
		consistency=self.Consistency(weight,eigenvalues)
		self.ReportLog(eigenvalues,eigenvector, weight, consistency)
		return 0


	def ReportLog(self, eigenvalues,eigenvector, weight, consistency):
		"Make a log output"
		log=" Weights: %s \n Consistency: %s" % (str([round(w,2) for w in weight]),consistency)
		self.EnvTEdit.setText(log)
		return 0


	def AddDecisionField(self,layer,Label):
		"""Add field on attribute table"""
		caps = layer.dataProvider().capabilities()
		if caps & QgsVectorDataProvider.AddAttributes:
			res = layer.dataProvider().addAttributes( [QgsField(Label, QVariant.Double,"",24,4,"")] )
		return 0


###########################################################################################
	def ExtractFieldSumSquare(self,field):
		"""Retrive single field value from attributes table"""
		provider=self.activeLayer.dataProvider()
		fid=provider.fieldNameIndex(field)
		listValue=[]
		for feat in self.activeLayer.getFeatures():
			attribute=feat.attributes()[fid]
			listValue.append(attribute)
		listValue=[pow(l,2) for l in listValue]
		return (sum(listValue)**(0.5))
	
	def StandardizationIdealPoint(self):
		"""Perform STEP 1 and STEP 2 of TOPSIS algorithm"""
		criteria=[self.EnvParameterWidget.horizontalHeaderItem(f).text() for f in range(self.EnvParameterWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		weight=[ round(w/sum(weight),4) for w in weight ]
		for c,w in zip(list(range(len(criteria))),weight):
			self.EnvParameterWidget.setItem(0,c,QTableWidgetItem(str(w))) 
		self.EnvGetWeightBtn.setEnabled(False)
		provider=self.activeLayer.dataProvider()
		feat = QgsFeature()
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		#self.EnvTEdit.append(str(dict(zip(fids,[(field) for field in criteria]))))
		sumSquareColumn=[self.ExtractFieldSumSquare(field) for field in criteria]
		
		matrix=[]
		for feat in self.activeLayer.getFeatures():
			row=[feat.attributes()[self.activeLayer.dataProvider().fieldNameIndex(name)] for  name in criteria]
			matrix.append(row)
		matrix=np.array(matrix, dtype = 'float32')
		matrixStd=[]
		for row in matrix:
			rowStd=[]
			for f,w,sSq in zip(row,weight,sumSquareColumn): #N.B. verifica corretto allineamento con i pesi
				value=(float(f)/float(sSq))*w   # TOPSIS algorithm: STEP 1 and STEP 2
				rowStd.append(value)
			matrixStd.append(rowStd)
		return matrixStd
		
			
	def RelativeCloseness(self, matrix):
		"""  distance from ideal point"""
		criteria=[self.EnvParameterWidget.horizontalHeaderItem(f).text() for f in range(self.EnvParameterWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		idealPoint=[float(self.EnvParameterWidget.item(2, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		sumSquareColumnList=[self.ExtractFieldSumSquare(field) for field in criteria]
		idealPoint=[float(self.EnvParameterWidget.item(2, c).text())/sumSquareColumnList[c]*weight[c] \
			for c in range(self.EnvParameterWidget.columnCount())]
		worstPoint=[float(self.EnvParameterWidget.item(3, c).text())/sumSquareColumnList[c]*weight[c] \
			for c in range(self.EnvParameterWidget.columnCount())]
		provider=self.activeLayer.dataProvider()

		if provider.fieldNameIndex("geoTOPSYS")==-1:
			self.AddDecisionField(self.activeLayer,"geoTOPSYS")
		fldValue = provider.fieldNameIndex("geoTOPSYS") #obtain classify field index from its name
		self.EnvTEdit.append("done") #   setText
		#self.EnvTEdit.append(str(idealPoint)+"#"+str(worstPoint))
		features=provider.featureCount() #Number of features in the layer.
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		##################################################################
		self.activeLayer.startEditing()
		self.EnvProgressBar.setRange(1,features)
		progress=0
		relativeClosenessList=[]
		for row in matrix:
			IP=WP=0
			for f,idp,wrp in zip(row,idealPoint,worstPoint):
				IP =IP+(float(f-idp)**2)   # TOPSIS algorithm: STEP 4
				WP =WP+(float(f-wrp)**2)
			relativeClosenessList.append((WP**(0.5))/((WP**(0.5))+(IP**(0.5))))
		for feat,relativeCloseness in zip(self.activeLayer.getFeatures(),relativeClosenessList):
			progress=progress+1
			self.activeLayer.changeAttributeValue(feat.id(), fldValue, round(float(relativeCloseness),4))
			self.EnvProgressBar.setValue(progress)
		self.activeLayer.commitChanges()
		self.EnvProgressBar.setValue(1)
		##################################################################
		return 0

###########################################################################################

	def Symbolize(self,fieldName):
		"""Prepare legends """
		numberOfClasses=self.spinBoxClasNum.value()
		if(numberOfClasses==5):
			classes=['very low', 'low','medium','high','very high']
		else:
			classes=list(range(1,numberOfClasses+1))
		layer = self.iface.activeLayer()
		provider = layer.dataProvider()
		fieldIndex=provider.fieldNameIndex(fieldName)
		minimum = provider.minimumValue( fieldIndex )
		maximum = provider.maximumValue( fieldIndex )
		RangeList = []
		Opacity = 1
		for c,i in zip(classes,list(range(len(classes)))):
		# Crea il simbolo ed il range...
			Min = minimum + ( maximum - minimum ) / numberOfClasses * i
			Max = minimum + ( maximum - minimum ) / numberOfClasses * ( i + 1 )
			Label = "%s [%.2f - %.2f]" % (c,Min,Max)
			Colour = QColor(255-255*i/numberOfClasses,255*i/numberOfClasses,0) #red to green
			Symbol = QgsSymbol.defaultSymbol(layer.geometryType())
			Symbol.setColor(Colour)
			#Symbol.setAlpha(Opacity)
			Range = QgsRendererRange(Min,Max,Symbol,Label)
			RangeList.append(Range)
		Renderer = QgsGraduatedSymbolRenderer('', RangeList)
		Renderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
		Renderer.setClassAttribute(fieldName)
		add=QgsVectorLayer(layer.source(),fieldName,'ogr')
		add.setRenderer(Renderer)
		QgsProject.instance().addMapLayer(add)


		
	def RenderLayer(self):
		""" Load thematic layers in canvas """
		fields=['geoTOPSYS']
		for f in fields:
			self.Symbolize(f)
		#self.setModal(False)

###########################################################################################
	
	def ExtractAttributeValue(self,field):
		"""Retrive single field value from attributes table"""
		fields=self.activeLayer.fields()
		provider=self.activeLayer.dataProvider()
		fid=provider.fieldNameIndex(field)
		listValue=[]
		if fields[fid].typeName()=='Real' or fields[fid].typeName()=='Integer':
			for feat in self.activeLayer.getFeatures():
				attribute=feat.attributes()[fid]
				listValue.append(float(attribute))
		else:
			for feat in self.activeLayer.getFeatures():
				attribute=feat.attributes()[fid]
				listValue.append(str(attribute))
		return listValue

	def BuildOutput(self):
		"""General function for all graphical and tabula output"""
		currentDir = str(os.path.abspath( os.path.dirname(__file__)))
		self.BuildHTML()
		webbrowser.open(os.path.join(currentDir,"barGraph.html"))
		#self.setModal(False)
		return 0

	
	def BuildHTML(self):
		geoTOPSISValue=self.ExtractAttributeValue('geoTOPSIS')
		geoTOPSISValue=[[A] for (A) in geoTOPSISValue]
		label=self.LabelListFieldsCBox.currentText()
		labels=self.ExtractAttributeValue(label)
		labels=[str(l) for l in labels]
		legend=['geoTOPSIS']
		htmlGraph.BuilHTMLGraph(geoTOPSISValue,labels,legend)
		return 0




###################################################################################################
	def about(self):
		"""
		Visualize an About window.
		"""
		QMessageBox.about(self, "About geoTOPIS model",
		"""
			<p>Performs geographic multi-criteria decision making using TOPIS model (Hwang, C.L.; Yoon, K. - 1981. Multiple Attribute Decision Making: Methods and Applications. New York: Springer-Verlag).
			Documents and data 	are available in <a href="http://maplab.alwaysdata.net/geomcda.html"> www.maplab.alwaysdata.net</a></p>
			<p>Author:  Gianluca Massei <a href="mailto:g_massa@libero.it">[g_massa at libero.it]</a></p>
		""")

	def open_help(self):
		webbrowser.open("http://maplab.alwaysdata.net/geomcda.html")
