import maya.cmds as cmds
import maya.mel as mm

import jpmSaveToFile_JSON as saveFile
import jpmRestoreFromFile_JSON as restoreFile
import jpmAmIaReference as ref

import os
import shutil
import functools

class jpmAnimWriter(object):
	def __init__(self):
		print "jpmAnimWriter"
		#True = alphabetical, False = creation time
		self.currentSort = True
		self.path = ""

	def setPathDialog(self, *args):
		cmds.fileBrowserDialog( m=4, fc=self.setPath, an='Set Anim Writer Path' )

	def setPath(self, fileName, fileType, *args):
		self.path = fileName + "/"
		self.populateFileList(self.currentSort)
		return 1
		
	def popUpName(self, fileListName, *args):
		#take the currently selected file and put it in the GUI's name field
		name = cmds.textScrollList( fileListName, q=1, si=1)[0]
		name,ext = os.path.splitext(name)
		cmds.textFieldGrp( "nameGrp", e=1, tx=name )
		
	def refreshRange(self, *args):
		poMin = cmds.playbackOptions( q=1, min=1)
		poMax = cmds.playbackOptions( q=1, max=1)
		cmds.floatFieldGrp( "animRange", e=1, v1=poMin, v2=poMax )
		
	def writeNewFile(self, *args):
		##fill the needed variables
		selectedTab = cmds.tabLayout( "tabs", q=1, st=1 )
		refReTarget = cmds.checkBox( "refReTargetCheck", q=1, v=1 )
		nodeNames = cmds.radioButtonGrp( "nodeNamesRadio", q=1, sl=1 )
		thisName = cmds.textFieldGrp( "nameGrp", q=1, tx=1 ) 
		selected = cmds.ls( sl=1 )
		
		fullname = self.path + thisName
		print fullname
		
		#try:
		##figure out which tab and which file is selected
		if selectedTab == "animFileForm":
			min = cmds.floatFieldGrp( "animRange", q=1, v1=1 ) 
			max = cmds.floatFieldGrp( "animRange", q=1, v2=1 ) 
			keyableAttrs = [""]
			fullname = fullname + ".nm8"
			saveType = ""
			saveFile.jpmSaveAnimationToFile(fullname, min, max, saveType, selected, keyableAttrs, refReTarget)
		if selectedTab == "poseFileForm":
			keyableAttrs = [""]
			fullname = fullname + ".psz"
			saveType = ""
			saveFile.jpmSavePoseToFile(fullname, saveType, selected, keyableAttrs, refReTarget)
		if selectedTab == "selFileForm":
			fullname = fullname + ".slc"
			saveFile.jpmSaveSelectionToFile(fullname, selected, refReTarget)
		self.populateFileList(self.currentSort)
		#except TypeError:
			#print "Uhh,... something has gone horribly wrong. Oh god, all the blood..."
		
	def applyFile(self, *args):
		##fill the needed variables
		selectedTab = cmds.tabLayout("tabs", q=1, st=1)
		refReTarget = cmds.checkBox("refReTargetCheck", q=1, v=1)
		selectionNumber = cmds.radioButtonGrp("selectionRadio", q=1, sl=1)
		if selectionNumber == 1:
			selectionType = "replace"
		if selectionNumber == 2:
			selectionType = "add"
		if selectionNumber == 3:
			selectionType = "toggle"
		if selectionNumber == 4:
			selectionType = "subtract"
		
		nodeNames = cmds.radioButtonGrp("nodeNamesRadio", q=1, sl=1)
		placeTime = 1
		placeValue = 0
		
		#try:
			##figure out which tab and which file is selected
		if selectedTab == "animFileForm":
			selectedFile = cmds.textScrollList("animFileList", q=1, si=1)[0]
		if selectedTab == "poseFileForm":
			selectedFile = cmds.textScrollList("poseFileList", q=1, si=1)[0]
		if selectedTab == "selFileForm":
			selectedFile = cmds.textScrollList("selFileList", q=1, si=1)[0]
			
		fullname = self.path + selectedFile
		print fullname
			
		##call the restore file procedure
		restoreFile.jpmRestoreFromFile(fullname, placeTime, placeValue, selectionType, refReTarget)
		#except TypeError:
		#	print "Pick a file"

	def deleteFile(self, *args):
		print "delete file"
		
	def renameFileWin(self, *args):
		print "rename file window"
		
	def populateFileList(self, alpha, *args):
		##get the path information
		##clear the file list
		##get a list of all files in the path
		##add each file to the appropriate file list
		cmds.optionVar( iv=("jpmAWalpha", alpha) )
		
		if self.path == "":
			self.setPathDialog()
		nmFiles = []
		pszFiles = []
		slcFiles = []
		cmds.textScrollList( "animFileList", e=1, ra=1 )
		cmds.textScrollList( "poseFileList", e=1, ra=1 )
		cmds.textScrollList( "selFileList", e=1, ra=1 )

		nmFiles = cmds.getFileList( fld=self.path, fs="*.nm8" )
		pszFiles = cmds.getFileList( fld=self.path, fs="*.psz" )
		slcFiles = cmds.getFileList( fld=self.path, fs="*.slc" )
		
		if alpha:
			if len(nmFiles) > 1:
				nmFiles.sort()
			if len(pszFiles) > 1:
				pszFiles.sort()
			if len(slcFiles) > 1:
				slcFiles.sort()
				
		if nmFiles != "":
			for nm in nmFiles:
				cmds.textScrollList( "animFileList", e=1, a=nm )		
		if pszFiles != "":
			for psz in pszFiles:
				cmds.textScrollList( "poseFileList", e=1, a=psz )
		if slcFiles != "":
			for slc in slcFiles:
				cmds.textScrollList( "selFileList", e=1, a=slc )
				
	def fieldsOnOff(self, *args):
		selectedTab = cmds.tabLayout( "tabs", q=1, st=1 )
		#print selectedTab
		if selectedTab == "animFileForm":
			cmds.floatFieldGrp( "animRange", e=1, en=1 ) 
			cmds.button( "refreshAnimRange", e=1, en=1 )
		else:
			cmds.floatFieldGrp( "animRange", e=1, en=0 ) 
			cmds.button( "refreshAnimRange", e=1, en=0 )
			
		if selectedTab == "settingsForm":
			cmds.textFieldGrp( "nameGrp", e=1, en=0 ) 
			cmds.button( "writeButton", e=1, en=0 )
		else: 
			cmds.textFieldGrp( "nameGrp", e=1, en=1 ) 
			cmds.button( "writeButton", e=1, en=1 )
			
		self.populateFileList(self.currentSort)

	def show(self, *args):
		verNum = 2.0
		winName = "jpmAnimWriter"
		if ( cmds.window( winName, exists=True) ):
			cmds.deleteUI( winName )
		cmds.window( winName, menuBar=1, t=("jpmAnimWriter v" + str(verNum) + "  --  James Parks"), rtf=True )
		
		if not cmds.optionVar(exists="jpmAWpath"):
			self.path = cmds.optionVar(q="jpmAWpath") + "/"
		if self.path == 0:
			self.setPathDialog()
			cmds.optionVar(self.path, sv="jpmAWpath")
		
		poMin = cmds.playbackOptions( q=1, min=1)
		poMax = cmds.playbackOptions( q=1, max=1)
		
		#Window menus
		fileMenu = cmds.menu( "fileMenu", l="File" )
		cmds.menuItem("setPathMenuItem", l="Set Path...", c=self.setPathDialog)
		cmds.menuItem("printPathMenuItem", l="Print Path", c=( "print \"" + self.path + "\"" ) )
		cmds.menuItem("writeNewMenuItem", l="Write New File", c=self.writeNewFile, p=fileMenu )
		cmds.menuItem("applyMenuItem", l="Apply Selected", c=self.applyFile, p=fileMenu )
		cmds.menuItem("refreshMenuItem", l="Refresh Window", c=self.show, p=fileMenu )
		
		sortMenu = cmds.menu( "sortMenu", l="Sort" )
		cmds.radioMenuItemCollection( "sortMethod" )
		cmds.menuItem( "listAlpha", l="Alpha", rb=self.currentSort, cl="sortMethod", c=functools.partial(self.populateFileList, True), p=sortMenu )
		cmds.menuItem( "listCreation", l="Creation", rb=(not self.currentSort), cl="sortMethod", c=functools.partial(self.populateFileList, False), p=sortMenu )
		
		#form and layout
		form = cmds.formLayout( "form", nd=100 )
		tabs = cmds.tabLayout("tabs", innerMarginWidth=5, innerMarginHeight=5, cc=self.fieldsOnOff)
		
		cmds.setParent(form)
		#name field and write new file button
		nameField = cmds.rowColumnLayout( nc=2, cw=([1,200],[2,80]) )
		cmds.textFieldGrp( "nameGrp", l="Name", cal=[1,"left"], tx="...File Name...", cw=([1,50],[2,150]) ) 
		cmds.button("writeButton", l="Write New File", w=100, c=self.writeNewFile)
		
		#min/max range fields
		cmds.floatFieldGrp( "animRange", nf=2 ,en=1, l="min/max", v1=poMin, v2=poMax, cal=[1,"left"], cw=([1,50],[2,75],[3,75]) ) 
		cmds.button( "refreshAnimRange", l="<--", ann="Refresh", en=1, w=20, c=self.refreshRange)

		cmds.setParent(tabs)
		#anim file list
		animFileForm = cmds.formLayout( "animFileForm", nd=100 )
		animFileList = cmds.textScrollList( "animFileList", ams=0, dcc=self.applyFile, dkc=self.deleteFile)
		
		#RMB pop up menu for the anim file list
		cmds.popupMenu( b=3, p=animFileList )
		cmds.menuItem( l="Apply Selected", c=self.applyFile)
		cmds.menuItem( l="Rename Selected...", c=self.renameFileWin)
		cmds.menuItem( l="Name --->", c=functools.partial(self.popUpName, "animFileList"))
		cmds.menuItem( divider=1 )
		cmds.menuItem( l="Delete Selected", c=self.deleteFile)
		
		cmds.setParent(tabs)
		#pose file list
		poseFileForm = cmds.formLayout( "poseFileForm", nd=100 )
		poseFileList = cmds.textScrollList( "poseFileList", ams=0, dcc=self.applyFile, dkc=self.deleteFile)
		
		#RMB pop up menu for the pose file list
		cmds.popupMenu( b=3, p=poseFileList )
		cmds.menuItem( l="Apply Selected", c=self.applyFile)
		cmds.menuItem( l="Rename Selected...", c=self.renameFileWin )
		cmds.menuItem( l="Name --->", c=functools.partial(self.popUpName, "poseFileList"))
		cmds.menuItem( divider=1 )
		cmds.menuItem( l="Delete Selected", c=self.deleteFile)
		
		cmds.setParent(tabs)
		#sel file list
		selFileForm = cmds.formLayout( "selFileForm", nd=100 )
		selFileList = cmds.textScrollList( "selFileList", ams=0, dcc=self.applyFile, dkc=self.deleteFile)
		
		#RMB pop up menu for the sel file list
		cmds.popupMenu( b=3, p=selFileList )
		cmds.menuItem( l="Apply Selected", c=self.applyFile)
		cmds.menuItem( l="Rename Selected...", c=self.renameFileWin)
		cmds.menuItem( l="Name --->", c=functools.partial(self.popUpName, "selFileList"))
		cmds.menuItem( divider=1 )
		cmds.menuItem( l="Delete Selected", c=self.deleteFile)
		
		selRadio = cmds.radioButtonGrp( "selectionRadio", nrb=4, cw=([1,60],[2,60],[3,60],[4,60]), la4=["replace", "add", "toggle", "subtract"], sl=1 )
		
		cmds.setParent(tabs)
		#settings tab
		settingsForm = cmds.formLayout( "settingsForm", nd=100 )
		settingsLayout = cmds.rowColumnLayout( nc=1 ,cw=[1,175] )
		refReTargetCheck = cmds.checkBox( "refReTargetCheck", l="Reference Re-Targeting", v=1, al="left" )
		nodeNamesRadio = cmds.radioButtonGrp( "nodeNamesRadio", nrb=2, cal=([1,"left"],[2,"left"]), cw=([1,75],[2,50],[3,50]),la2=["Short", "Long"], l="Node Names", sl=1 )
		overwriteCheck = cmds.checkBox( "overwriteCheck", l="Overwrite Protection", v=0, al="left" )
		deleteStaticCheck = cmds.checkBox( "deleteStaticCheck", l="Delete Static Channels", v=0, al="left" )
		
		cmds.setParent(form)
		#apply selected button
		applyButton = cmds.button( "applyButton", l="Apply Selected", w=100, c=self.applyFile)
		
		cmds.tabLayout( tabs, edit=True, tabLabel=((animFileForm, 'Anim'), (poseFileForm, 'Pose'), (selFileForm, 'Sel'),(settingsForm, "Settings")) )
		##form attaches
		cmds.formLayout( form, e=1, af=([tabs,"top",50],[tabs,"left",0],[tabs,"bottom",25],[tabs,"right",0]) )
		cmds.formLayout( form, e=1, af=([nameField,"top",0],[nameField,"left",0],[nameField,"right",0]) )
		cmds.formLayout( animFileForm, e=1, af=([animFileList,"top",0],[animFileList,"left",0],[animFileList,"bottom",0],[animFileList,"right",0]) )
		cmds.formLayout( poseFileForm, e=1, af=([poseFileList,"top",0],[poseFileList,"left",0],[poseFileList,"bottom",0],[poseFileList,"right",0]) )
		cmds.formLayout( selFileForm, e=1, af=([selFileList,"top",0],[selFileList,"left",0],[selFileList,"bottom",25],[selFileList,"right",0]) )
		cmds.formLayout( selFileForm, e=1, af=([selRadio,"bottom",0],[selRadio,"left",0],[selRadio,"right",0]) )
		cmds.formLayout( settingsForm, e=1, af=([settingsLayout,"top",0],[settingsLayout,"left",0],[settingsLayout,"bottom",0],[settingsLayout,"right",0] ) )
		cmds.formLayout( form, e=1, af=([applyButton,"left",0],[applyButton,"bottom",0],[applyButton,"right",0]) )

		self.populateFileList(self.currentSort)
		
		cmds.showWindow( winName )