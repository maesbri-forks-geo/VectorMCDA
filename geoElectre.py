# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name			: geoConcordance
Description		: geographical MCDA with Electre model (ranking with concordance and discordance index)
Date			: June 20, 2014
copyright		: (C) 2018 by Gianluca Massei
email			: (g_massa@libero.it)

 ***************************************************************************/

/***************************************************************************
 *																		 *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.    			   *
 *																		 *
 ***************************************************************************/
"""
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QMenu
from qgis.PyQt import QtGui
from qgis.core import *
from qgis.gui import *


import os
import webbrowser
from . import htmlGraph
import csv

try:
	import matplotlib.pyplot as plt
	import numpy as np
except ImportError as e:
	QMessageBox.information(None, QCoreApplication.translate('geoConcordance', "Plugin error"), \
	QCoreApplication.translate('geoConcordance', "Couldn't import Python module. [Message: %s]" % e))
	

from .ui_geoElectre import Ui_Dialog

class geoElectreDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		QDialog.__init__(self, iface.mainWindow())
		self.setupUi(self)
		self.iface = iface
		self.activeLayer = self.iface.activeLayer()
		#self.base_Layer = self.iface.activeLayer()
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,False)

#		QObject.connect(self.SetBtnQuit, SIGNAL("clicked()"),self, SLOT("reject()"))
		self.SetBtnQuit.clicked.connect(self.reject)
		self.SetBtnAbout.clicked.connect(self.about)
		self.SetBtnHelp.clicked.connect(self.open_help) 
#		QObject.connect(self.EnvAddFieldBtn, SIGNAL( "clicked()" ), self.AddField)
		self.EnvGetWeightBtn.clicked.connect(self.elaborateAttributeTable)
		self.EnvCalculateBtn.clicked.connect(self.analyticHierarchyProcess)
		self.RenderBtn.clicked.connect(self.renderLayer)
		self.GraphBtn.clicked.connect(self.buildOutput)
#		QObject.connect(self.AnlsBtnBox, SIGNAL("rejected()"),self, SLOT("reject()"))
		self.AnlsBtnBox.clicked.connect(self.reject)
		
		sourceIn=str(self.iface.activeLayer().source())
		#self.baseLbl.setText(sourceIn)
		pathSource=os.path.dirname(sourceIn)
		outFile="geoConcordance.shp"
		sourceOut=os.path.join(pathSource,outFile)
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
		EnvSetLabel=["Weigths","Preference"]
		self.EnvParameterWidget.setColumnCount(len(Envfields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvParameterWidget.setRowCount(2)
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)
		for r in range(len(Envfields)):
			self.EnvTableWidget.setItem(r,r,QTableWidgetItem("1.0"))
			self.EnvParameterWidget.setItem(0,r,QTableWidgetItem("1.0"))
			self.EnvParameterWidget.setItem(1,r,QTableWidgetItem("gain"))
		#retrieve signal for modified cell
		self.EnvTableWidget.cellChanged[(int,int)].connect(self.completeMatrix)
		self.EnvParameterWidget.cellClicked[(int,int)].connect(self.changeValue)
###############################ContextMenu########################################
		headers = self.EnvParameterWidget.horizontalHeader()
		headers.setContextMenuPolicy(Qt.CustomContextMenu)
		headers.customContextMenuRequested.connect(self.popMenu)
#################################################################################
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,True)
		#setting=self.csv2setting()
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
		if not outvLayer.isEmpty():
			self.OutlEdt.clear()
			self.OutlEdt.insert(outvLayer)
		return outvLayer


	def updateTable(self):
		"""Prepare and compile tbale in GUI"""
		pathSource=os.path.dirname(str(self.iface.activeLayer().source()))
		Envfields=[f for f in self.GetFieldNames(self.activeLayer)]
#######################################################################################
		self.EnvTableWidget.setColumnCount(len(Envfields))
		self.EnvTableWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvTableWidget.setRowCount(len(Envfields))
		self.EnvTableWidget.setVerticalHeaderLabels(Envfields)

		EnvSetLabel=["Weigths","Preference"]
		self.EnvParameterWidget.setColumnCount(len(Envfields))
		self.EnvParameterWidget.setHorizontalHeaderLabels(Envfields)
		self.EnvParameterWidget.setRowCount(2)
		self.EnvParameterWidget.setVerticalHeaderLabels(EnvSetLabel)

		for r in range(len(Envfields)):
			self.EnvParameterWidget.setItem(0,r,QTableWidgetItem("1.0"))
			self.EnvParameterWidget.setItem(1,r,QTableWidgetItem("gain"))
		return 0


	def popMenu(self):
		fields=list(range(10))
		menu = QMenu()
		removeAction = menu.addAction("Remove selected fields")
		reloadAllFields=menu.addAction("Add deleted fields")
		action = menu.exec_(self.mapToGlobal(QPoint(100,100)))
		if action == removeAction:
			self.removePopup()
		elif action==reloadAllFields:
			self.addPopup()
			

	def addPopup(self):
		Envfields=self.GetFieldNames(self.activeLayer) #field list
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		difference=set(Envfields)-set(criteria)
		for f in difference:
			self.addField(f)
			
			
	def removePopup(self):
		selected = sorted(self.EnvParameterWidget.selectionModel().selectedColumns(),reverse=True)
		if len(selected) > 0:
			for s in selected:
				self.removeField(s.column())
			self.EnvParameterWidget.setCurrentCell(-1,-1)
		else:
			QMessageBox.warning(self.iface.mainWindow(), "geoConcordance",
			("column must to be selected"), QMessageBox.Ok, QMessageBox.Ok)
		return 0


	def removeField(self,i):
		"""Remove field in table in GUI"""
		self.EnvTableWidget.removeColumn(i)
		self.EnvTableWidget.removeRow(i)
		self.EnvParameterWidget.removeColumn(i)
		return 0


	def addField(self,f=''):
		"""Add field to table in GUI"""
		if f=='':
			f=self.EnvlistFieldsCBox.currentText()
		self.EnvTableWidget.insertColumn(self.EnvTableWidget.columnCount())
		self.EnvTableWidget.insertRow(self.EnvTableWidget.rowCount())
		self.EnvTableWidget.setHorizontalHeaderItem((self.EnvTableWidget.columnCount()-1),QTableWidgetItem(f))
		self.EnvTableWidget.setVerticalHeaderItem((self.EnvTableWidget.rowCount()-1),QTableWidgetItem(f))

		self.EnvParameterWidget.insertColumn(self.EnvParameterWidget.columnCount())
		self.EnvParameterWidget.setHorizontalHeaderItem((self.EnvParameterWidget.columnCount()-1),QTableWidgetItem(f))
		self.EnvParameterWidget.setItem(0,(self.EnvParameterWidget.columnCount()-1),QTableWidgetItem("1.0"))
		self.EnvParameterWidget.setItem(1,(self.EnvParameterWidget.columnCount()-1),QTableWidgetItem("gain"))
		return 0



	def completeMatrix(self):
		"""Autocomplete matrix of  pairwise comparison"""
		try:
			cell=self.EnvTableWidget.currentItem()
			if cell.text()!=None and type(float(cell.text())==float):
				val=round(float(cell.text())**(-1),2)
				self.EnvTableWidget.setItem(cell.column(),cell.row(),QTableWidgetItem(str(val)))
			return 0
		except ValueError:
			QMessageBox.warning(self.iface.mainWindow(), "geoWeightedSum",
			("Input error\n" "Please insert numeric value "\
			"active"), QMessageBox.Ok, QMessageBox.Ok)


	def changeValue(self):
		"""Event for change gain/cost"""
		cell=self.EnvParameterWidget.currentItem()
		val=cell.text()
		if val=="cost":
			self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
		elif val=="gain":
			self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
		else:
			self.EnvParameterWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
		return 0

	def calculateWeight(self,pairwise):
		"Define vector of weight based on eigenvector and eigenvalues"
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
		return weight, eigenvalues,  eigenvector


	def Consistency(self,weight,eigenvalues):
		"Calculete Consistency index in accord with Saaty (1977)"
		try:
			RI=[0.00, 0.00, 0.00,0.52,0.90,1.12,1.24,1.32,1.41]	 #order of matrix: 0,1,2,3,4,5,6,7,8
			order=len(weight)
			CI=(np.max(eigenvalues)-order)/(order-1)
			return CI/RI[order-1]
		except:
			return 1.41

	def analyticHierarchyProcess(self):
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
			res = layer.dataProvider().addAttributes( [QgsField(Label, QVariant.Double) ] )
		return 0
		


	def Attributes2Matrix(self):
		matrix=[]
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		preference=[str(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		provider=self.activeLayer.dataProvider()
		features= self.activeLayer.getFeatures()
		for feat in features:
			row=[feat.attributes()[provider.fieldNameIndex(name)] for  name in criteria]
			matrix.append(row)
		matrix=np.array(matrix, dtype = 'float32')
		return matrix
	
	def setting2csv(self):
		currentDIR = (os.path.dirname(str(self.activeLayer.source())))
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		preference=[str(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		csvFile=open(os.path.join(currentDIR,'setConcordance.csv'),"wb")
		write=csv.writer(csvFile,delimiter=";",quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
		write.writerow(criteria)
		write.writerow(weight)
		write.writerow(preference)
		csvFile.close()
		
	def csv2setting(self):
		currentDIR = (os.path.dirname(str(self.activeLayer.source())))
		setting=[]
		try:
			with open(os.path.join(currentDIR,'setConcordance.csv')) as csvFile:
				csvReader = csv.reader(csvFile, delimiter=";", quotechar='"')
				for row in csvReader:
					setting.append(row)
			return setting
		except:
			QgsMessageLog.logMessage("Problem in reading setting file","geo",QgsMessageLog.WARNING)

	def setting2table(self,setting):
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		for i in range(len(criteria)):
			for l in range(len(setting[0])):
				if criteria[i]==setting[0][l]:
					self.EnvParameterWidget.setItem(0,i,QTableWidgetItem(str(setting[1][l])))
					self.EnvParameterWidget.setItem(1,i,QTableWidgetItem(str(setting[2][l])))
					
	
	def StandardizeMatrix(self,preference,weight,matrix,minField,maxField):
		""" """
		StdMatrix=[]
		for row in matrix:
			List=[]
			for r,minF, maxF, pref, wgt  in zip(row, minField,maxField,preference,weight):
				if pref=='gain':
					value=((r-minF)/(maxF-minF)) #cres: x-min / max - min
				else:
					value=((maxF-r)/(maxF-minF))  #dec: max-x / max-min
				List.append(value)
			StdMatrix.append(List)
		return StdMatrix
	
	def ConcordanceMatrix(self, matrix,weight):
		concordance=[]
		for row1 in matrix:
			crow=[]
			for row2 in matrix:
				value=0
				for r1,r2,w in zip(row1,row2,weight):
					if r1>r2:
						value=value+w
				crow.append(value)
			concordance.append(crow)
		return concordance

	def DiscordanceMatrix(self, matrix):
		discordance=[]
		for row1 in matrix:
			drow=[]
			value=0
			for row2 in matrix:
				for r1,r2 in zip(row1,row2):
					if (r1-r2)>value:
						value=(r1-r2)
					else:
						value=value
				drow.append(value)
			discordance.append(drow)
		return discordance
		
	
	def ConcordanceIndex(self,concordance):
		concIndx=[]
		concordance=np.array(concordance, dtype = 'float32')
		for i in range(len(concordance)):
			row=concordance[i]
			col=concordance[:,i]
			value=sum(row)-sum(col)
			concIndx.append(value)
		return concIndx
		
	def DiscordanceIndex(self,discordance):
		discIndx=[]
		discordance=np.array(discordance, dtype = 'float32')
		for i in range(len(discordance[0])):
			row=discordance[i]
			col=discordance[:,i]
			value=sum(row)-sum(col)
			discIndx.append(value)
		return discIndx
	

		
	def elaborateAttributeTable(self):
		"""Standardization fields values in range [0-1]"""
		criteria=[self.EnvTableWidget.verticalHeaderItem(f).text() for f in range(self.EnvTableWidget.columnCount())]
		weight=[float(self.EnvParameterWidget.item(0, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		preference=[str(self.EnvParameterWidget.item(1, c).text()) for c in range(self.EnvParameterWidget.columnCount())]
		provider=self.activeLayer.dataProvider()
		if provider.fieldNameIndex("geoConc")==-1:
			self.AddDecisionField(self.activeLayer,"geoConc")
		fldConcValue = provider.fieldNameIndex("geoConc") #obtain classify field index from its name
		if provider.fieldNameIndex("geoDisc")==-1:
			self.AddDecisionField(self.activeLayer,"geoDisc")
		fldDiscValue = provider.fieldNameIndex("geoDisc") #obtain classify field index from its name
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		minField=[provider.minimumValue( f ) for f in fids]
		maxField=[provider.maximumValue( f ) for f in fids]

		matrix= self.Attributes2Matrix()
		
		matrix=self.StandardizeMatrix(preference,weight,matrix,minField,maxField)
		#print '\n'+str(matrix)
		concordanceMatrix=self.ConcordanceMatrix(matrix,weight)
		discordanceMatrix=self.DiscordanceMatrix(matrix)
		#print concordanceMatrix,discordanceMatrix
		
		concIndx=self.ConcordanceIndex(concordanceMatrix)
		discIndx=self.DiscordanceIndex(discordanceMatrix)
		progress=0
		self.EnvProgressBar.setRange(1,provider.featureCount())
		self.activeLayer.startEditing()
		for conc,disc,feat in zip(concIndx,discIndx,self.activeLayer.getFeatures()):
			progress=progress+1
			self.activeLayer.changeAttributeValue(feat.id(),fldConcValue,round(float(conc),4))
			self.activeLayer.changeAttributeValue(feat.id(),fldDiscValue,round(float(disc),4))
			self.EnvProgressBar.setValue(progress)
		self.activeLayer.commitChanges()
		self.EnvTEdit.append("done") 
		return 0




	def symbolize(self,fieldName):
		"""Prepare legends """
		numberOfClasses=self.spinBoxClasNum.value()
		if(numberOfClasses==5):
			classes=['very low', 'low','medium','high','very high']
		else:
			classes=list(range(1,numberOfClasses+1))
		numberOfClasses=len(classes)
		layer = self.iface.activeLayer()
		fieldIndex = layer.fields().indexFromName(fieldName)
		provider = layer.dataProvider()
		minimum = provider.minimumValue( fieldIndex )
		maximum = provider.maximumValue( fieldIndex )
		print(minimum,maximum)
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


	def renderLayer(self):
		""" Load thematic layers in canvas """
		fields=['geoConc','geoDisc']
		for f in fields:
			self.symbolize(f)
		#self.setModal(False)

###########################################################################################


	def extractAttributeValue(self,field):
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




	def buildOutput(self):
		"""General function for all graphical and tabula output"""
		currentDir = str(os.path.abspath( os.path.dirname(__file__)))
		if os.path.isfile(os.path.join(currentDir,"histogram.png"))==True:
			os.remove(os.path.join(currentDir,"histogram.png"))
		try:
			import matplotlib.pyplot as plt
			import numpy as np
			#self.BuildGraphPnt(currentDir)
			self.buildGraphIstogram(currentDir)
		except ImportError as e:
			QMessageBox.information(None, QCoreApplication.translate('geoConcordance', "Plugin error"), \
			QCoreApplication.translate('geoConcordance', "Couldn't import Python modules 'matplotlib' and 'numpy'. [Message: %s]" % e))
		self.buildHTML()
		webbrowser.open(os.path.join(currentDir,"barGraph.html"))
		#self.setModal(False)
		return 0



	def buildGraphIstogram(self,currentDir):
		"""Build Istogram graph using pyplot"""
		geoConcValue=self.extractAttributeValue('geoConc')
		geoDiscValue=self.extractAttributeValue('geoDisc')
		fig = plt.figure()
		fig.subplots_adjust(bottom=0.2)
		fig.subplots_adjust()
		ax = fig.add_subplot(111)
		ax.margins(0.05, None)
		xpos = np.arange(len(geoConcValue))    # the x locations for the groups
		width = 0.35    # the width of the bars: can also be len(x) sequence
		label=self.LabelListFieldsCBox.currentText()
		labels=self.extractAttributeValue(label)
		p1 = plt.bar((xpos), geoConcValue, width, color='g',align='center') 
		p2 = plt.bar((xpos+width), geoDiscValue, width, color='r', align='center') 
		plt.ylabel('Scores')
		plt.title('geoConcordance')
		plt.xticks((xpos), tuple(labels),rotation=90,fontsize=6 )
		plt.legend((p1[0], p2[0]), ('geoConcordamce', 'geoDiscordance'))
		plt.savefig(os.path.join(currentDir,"histogram.png"))
		self.LblGraphic.setPixmap(QtGui.QPixmap(os.path.join(currentDir,"histogram.png")))
		plt.close('all')
		return 0

	
	def buildHTML(self):
		geoConcValue=self.extractAttributeValue('geoConc')
		geoDiscValue=self.extractAttributeValue('geoDisc')
		geoConcordanceValue=[[A,B] for (A,B) in zip(geoConcValue,geoDiscValue)]
		label=self.LabelListFieldsCBox.currentText()
		labels=self.extractAttributeValue(label)
		labels=[str(l) for l in labels]
		legend=['geoConcordance','geoDiscordance']
		htmlGraph.BuilHTMLGraph(geoConcordanceValue,labels,legend)
		return 0




###################################################################################################
	def about(self):
		"""
		Visualize an About window.
		"""

		QMessageBox.about(self, "About geoConcordance and geoDiscordance models",
		"""
		<p>Performs geographic multi-criteria decision making using concordance and discordance model (Bernard Roy, Classement et choix en presence de points de vue multiples (la methode ELECTRE), in La Revue d'Informatique et de Recherche Operationelle (RIRO), nr 8, 1968, pp. 57-75).
		Documents and data 	are available in: <a href="http://maplab.alwaysdata.net/geomcda.html"> www.maplab.alwaysdata.net</a></p>
		<p>Author:  Gianluca Massei <a href="mailto:g_massa@libero.it">[g_massa at libero.it]</a></p>
		""")

	def open_help(self):
		webbrowser.open("http://maplab.alwaysdata.net/geomcda.html")

