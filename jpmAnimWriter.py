import maya.cmds as cmds
import maya.mel as mm
import jpmSaveToFile_JSON as saveFile
import jpmRestoreFromFile as restoreFile
import jpmAmIaReference as ref
import os
import shutil


def jpmAW_setPathDialog():
	cmds.fileBrowserDialog( m=4, fc=jpmAW_setPath, an='Set Anim Writer Path' )

def jpmAW_setPath( fileName, fileType):
	cmds.optionVar( sv=["jpmAWpath",fileName] );
	currentSort = cmds.optionVar( q="jpmAWalpha" )
	jpmAW_populateFileList(currentSort)
	return 1
	
def jpmAW_popUpName(fileListName):
	#take the currently selected file and put it in the GUI's name field
	name = cmds.textScrollList( fileListName, q=1, si=1)[0]
	name,ext = os.path.splitext(name)
	cmds.textFieldGrp( "jpmAW_nameGrp", e=1, tx=name )
	
def jpmAW_refreshRange():
	poMin = cmds.playbackOptions( q=1, min=1)
	poMax = cmds.playbackOptions( q=1, max=1)
	cmds.floatFieldGrp( "jpmAW_animRange", e=1, v1=poMin, v2=poMax )
	
def jpmAW_writeNewFile():
	##fill the needed variables
	path = cmds.optionVar( q="jpmAWpath" )## + "/"
	currentSort = cmds.optionVar( q="jpmAWalpha" )
	selectedTab = cmds.tabLayout( "jpmAW_tabs", q=1, st=1 )
	refReTarget = cmds.checkBox( "jpmAW_refReTargetCheck", q=1, v=1 )
	nodeNames = cmds.radioButtonGrp( "jpmAW_nodeNamesRadio", q=1, sl=1 )
	thisName = cmds.textFieldGrp( "jpmAW_nameGrp", q=1, tx=1 ) 
	selected = cmds.ls( sl=1 )
	
	fullname = path + "/" + thisName
	print fullname
	
	try:
		##figure out which tab and which file is selected
		if selectedTab == "animFileForm":
			min = cmds.floatFieldGrp( "jpmAW_animRange", q=1, v1=1 ) 
			max = cmds.floatFieldGrp( "jpmAW_animRange", q=1, v2=1 ) 
			keyableAttrs = [""]
			fullname = fullname + ".nm8"
			saveType = ""
			saveFile.jpmSaveAnimationToFile(fullname, min, max, saveType, selected, keyableAttrs, refReTarget)
		if selectedTab == "poseFileForm":
			keyableAttrs = [""]
			fullname = fullname + ".psz"
			saveFile.jpmSavePoseToFile(fullname, selected, keyableAttrs, refReTarget)
		if selectedTab == "selFileForm":
			fullname = fullname + ".slc"
			saveFile.jpmSaveSelectionToFile(fullname, selected, refReTarget)
		jpmAW_populateFileList(currentSort)
	except TypeError:
		print "Uhh,... something has gone horribly wrong. Oh god, all the blood..."
	
def jpmAW_applyFile():
	##fill the needed variables
	path = cmds.optionVar( q="jpmAWpath" ) + "/"
	selectedTab = cmds.tabLayout( "jpmAW_tabs", q=1, st=1 )
	refReTarget = cmds.checkBox( "jpmAW_refReTargetCheck", q=1, v=1 )
	selectionNumber = cmds.radioButtonGrp( "jpmAW_selectionRadio", q=1, sl=1 )
	if selectionNumber == 1:
		selectionType = "replace"
	if selectionNumber == 2:
		selectionType = "add"
	if selectionNumber == 3:
		selectionType = "toggle"
	if selectionNumber == 4:
		selectionType = "subtract"
	
	nodeNames = cmds.radioButtonGrp( "jpmAW_nodeNamesRadio", q=1, sl=1 )
	placeTime = 1
	placeValue = 0
	
	try:
		##figure out which tab and which file is selected
		if selectedTab == "animFileForm":
			selectedFile = cmds.textScrollList( "jpmAW_animFileList", q=1, si=1 )[0]
		if selectedTab == "poseFileForm":
			selectedFile = cmds.textScrollList( "jpmAW_poseFileList", q=1, si=1 )[0]
		if selectedTab == "selFileForm":
			selectedFile = cmds.textScrollList( "jpmAW_selFileList", q=1, si=1 )[0]
			
		fullname = path + selectedFile
		print fullname
			
		##call the restore file procedure
		restoreFile.jpmRestoreFromFile(fullname, placeTime, placeValue, selectionType, refReTarget)
	except TypeError:
		print "Pick a file"

def jpmAW_deleteFile():
	print "delete file"
	
def jpmAW_renameFileWin():
	print "rename file window"
	
def jpmAW_populateFileList(alpha):
	##get the path information
	##clear the file list
	##get a list of all files in the path
	##add each file to the appropriate file list
	
	path = cmds.optionVar( q="jpmAWpath" ) + "/"
	cmds.optionVar( iv=("jpmAWalpha", alpha) )
	
	if path == 0:
		jpmAW_setPathDialog()
	nmFiles = []
	pszFiles = []
	slcFiles = []
	cmds.textScrollList( "jpmAW_animFileList", e=1, ra=1 )
	cmds.textScrollList( "jpmAW_poseFileList", e=1, ra=1 )
	cmds.textScrollList( "jpmAW_selFileList", e=1, ra=1 )

	nmFiles = cmds.getFileList( fld=path, fs="*.nm8" )
	pszFiles = cmds.getFileList( fld=path, fs="*.psz" )
	slcFiles = cmds.getFileList( fld=path, fs="*.slc" )
	
	if alpha:
		if len(nmFiles) > 1:
			nmFiles.sort()
		if len(pszFiles) > 1:
			pszFiles.sort()
		if len(slcFiles) > 1:
			slcFiles.sort()
			
	if nmFiles != "":
		for nm in nmFiles:
			cmds.textScrollList( "jpmAW_animFileList", e=1, a=nm )		
	if pszFiles != "":
		for psz in pszFiles:
			cmds.textScrollList( "jpmAW_poseFileList", e=1, a=psz )
	if slcFiles != "":
		for slc in slcFiles:
			cmds.textScrollList( "jpmAW_selFileList", e=1, a=slc )
			
def jpmAW_fieldsOnOff():
	currentSort = 1
	currentSort = cmds.optionVar( q="jpmAWalpha" )
	selectedTab = cmds.tabLayout( "jpmAW_tabs", q=1, st=1 )
	#print selectedTab
	if selectedTab == "animFileForm":
		cmds.floatFieldGrp( "jpmAW_animRange", e=1, en=1 ) 
		cmds.button( "refreshAnimRange", e=1, en=1 )
	else:
		cmds.floatFieldGrp( "jpmAW_animRange", e=1, en=0 ) 
		cmds.button( "refreshAnimRange", e=1, en=0 )
		
	if selectedTab == "settingsForm":
		cmds.textFieldGrp( "jpmAW_nameGrp", e=1, en=0 ) 
		cmds.button( "jpmAW_writeButton", e=1, en=0 )
	else: 
		cmds.textFieldGrp( "jpmAW_nameGrp", e=1, en=1 ) 
		cmds.button( "jpmAW_writeButton", e=1, en=1 )
		
	jpmAW_populateFileList(currentSort)

def jpmAnimWriter():
	verNum = 2.0
	winName = "jpmAnimWriter"
	if ( cmds.window( winName, exists=True) ):
		cmds.deleteUI( winName )
	cmds.window( winName, menuBar=1, t=("jpmAnimWriter v" + str(verNum) + "  --  James Parks"), rtf=True )
	
	path = cmds.optionVar(q="jpmAWpath")
	if path == 0:
		jpmAW_setPathDialog()
	path = cmds.optionVar( q="jpmAWpath" ) + "/"
	
	
	currentSort = 1
	currentSort = cmds.optionVar( q="jpmAWalpha" )
	poMin = cmds.playbackOptions( q=1, min=1)
	poMax = cmds.playbackOptions( q=1, max=1)
	
	#Window menus
	jpmAW_fileMenu = cmds.menu( "jpmAW_fileMenu", l="File" )
	cmds.menuItem( "jpmAW_setPathMenuItem", l="Set Path...", c="jpmAW_setPathDialog()" )
	cmds.menuItem( "jpmAW_printPathMenuItem", l="Print Path", c=( "print \"" + path + "\"" ) )
	cmds.menuItem( "jpmAW_writeNewMenuItem", l="Write New File", c="jpmSaveToFile()", p=jpmAW_fileMenu )
	cmds.menuItem( "jpmAW_applyMenuItem", l="Apply Selected", c="jpmARestoreFromFile()", p=jpmAW_fileMenu )
	cmds.menuItem( "jpmAW_refreshMenuItem", l="Refresh Window", c="jpmAnimWriter()", p=jpmAW_fileMenu )
	
	jpmAW_sortMenu = cmds.menu( "jpmAW_sortMenu", l="Sort" )
	cmds.radioMenuItemCollection( "jpmAW_sortMethod" )
	cmds.menuItem( "jpmAW_listAlpha", l="Alpha", rb=currentSort, cl="jpmAW_sortMethod", c="jpmAW_populateFileList(1)", p=jpmAW_sortMenu )
	cmds.menuItem( "jpmAW_listCreation", l="Creation", rb=(not currentSort), cl="jpmAW_sortMethod", c="jpmAW_populateFileList(0)", p=jpmAW_sortMenu )
	
	#form and layout
	jpmAW_form = cmds.formLayout( "jpmAW_form", nd=100 )
	tabs = cmds.tabLayout( "jpmAW_tabs", innerMarginWidth=5, innerMarginHeight=5, cc="jpmAW_fieldsOnOff()" )
	
	cmds.setParent(jpmAW_form)
	#name field and write new file button
	jpmAW_nameField = cmds.rowColumnLayout( nc=2, cw=([1,200],[2,80]) )
	cmds.textFieldGrp( "jpmAW_nameGrp", l="Name", cal=[1,"left"], tx="...File Name...", cw=([1,50],[2,150]) ) 
	cmds.button( "jpmAW_writeButton", l="Write New File", w=100, c="jpmAW_writeNewFile()" )
	
	#min/max range fields
	cmds.floatFieldGrp( "jpmAW_animRange", nf=2 ,en=1, l="min/max", v1=poMin, v2=poMax, cal=[1,"left"], cw=([1,50],[2,75],[3,75]) ) 
	cmds.button( "refreshAnimRange", l="<--", ann="Refresh", en=1, w=20, c=("jpmAW_refreshRange()") )

	cmds.setParent(tabs)
	#anim file list
	animFileForm = cmds.formLayout( "animFileForm", nd=100 )
	animFileList = cmds.textScrollList( "jpmAW_animFileList", ams=0, dcc="jpmAW_applyFile()", dkc="jpmAW_deleteFile()" )
	
	#RMB pop up menu for the anim file list
	cmds.popupMenu( b=3, p=animFileList )
	cmds.menuItem( l="Apply Selected", c="jpmAW_applyFile()" )
	cmds.menuItem( l="Rename Selected...", c="jpmAW_renameFileWin()" )
	cmds.menuItem( l="Name --->", c="jpmAW_popUpName(\"jpmAW_animFileList\")" )
	cmds.menuItem( divider=1 )
	cmds.menuItem( l="Delete Selected", c="jpmAW_deleteFile()" )
	
	cmds.setParent(tabs)
	#pose file list
	poseFileForm = cmds.formLayout( "poseFileForm", nd=100 )
	poseFileList = cmds.textScrollList( "jpmAW_poseFileList", ams=0, dcc="jpmAW_applyFile()", dkc="jpmAW_deleteFile()" )
	
	#RMB pop up menu for the pose file list
	cmds.popupMenu( b=3, p=poseFileList )
	cmds.menuItem( l="Apply Selected", c="jpmAW_applyFile()" )
	cmds.menuItem( l="Rename Selected...", c="jpmAW_renameFileWin()" )
	cmds.menuItem( l="Name --->", c="jpmAW_popUpName(\"jpmAW_poseFileList\")" )
	cmds.menuItem( divider=1 )
	cmds.menuItem( l="Delete Selected", c="jpmAW_deleteFile()" )
	
	cmds.setParent(tabs)
	#sel file list
	selFileForm = cmds.formLayout( "selFileForm", nd=100 )
	selFileList = cmds.textScrollList( "jpmAW_selFileList", ams=0, dcc="jpmAW_applyFile()", dkc="jpmAW_deleteFile()" )
	
	#RMB pop up menu for the sel file list
	cmds.popupMenu( b=3, p=selFileList )
	cmds.menuItem( l="Apply Selected", c="jpmAW_applyFile()" )
	cmds.menuItem( l="Rename Selected...", c="jpmAW_renameFileWin()" )
	cmds.menuItem( l="Name --->", c="jpmAW_popUpName(\"jpmAW_selFileList\")" )
	cmds.menuItem( divider=1 )
	cmds.menuItem( l="Delete Selected", c="jpmAW_deleteFile()" )
	
	selRadio = cmds.radioButtonGrp( "jpmAW_selectionRadio", nrb=4, cw=([1,60],[2,60],[3,60],[4,60]), la4=["replace", "add", "toggle", "subtract"], sl=1 )
	
	cmds.setParent(tabs)
	#settings tab
	settingsForm = cmds.formLayout( "settingsForm", nd=100 )
	settingsLayout = cmds.rowColumnLayout( nc=1 ,cw=[1,175] )
	refReTargetCheck = cmds.checkBox( "jpmAW_refReTargetCheck", l="Reference Re-Targeting", v=1, al="left" )
	nodeNamesRadio = cmds.radioButtonGrp( "jpmAW_nodeNamesRadio", nrb=2, cal=([1,"left"],[2,"left"]), cw=([1,75],[2,50],[3,50]),la2=["Short", "Long"], l="Node Names", sl=1 )
	overwriteCheck = cmds.checkBox( "jpmAW_overwriteCheck", l="Overwrite Protection", v=0, al="left" )
	deleteStaticCheck = cmds.checkBox( "jpmAW_deleteStaticCheck", l="Delete Static Channels", v=0, al="left" )
	
	cmds.setParent(jpmAW_form)
	#apply selected button
	applyButton = cmds.button( "jpmAW_applyButton", l="Apply Selected", w=100, c="jpmAW_applyFile()" )
	
	cmds.tabLayout( tabs, edit=True, tabLabel=((animFileForm, 'Anim'), (poseFileForm, 'Pose'), (selFileForm, 'Sel'),(settingsForm, "Settings")) )
	##form attaches
	cmds.formLayout( jpmAW_form, e=1, af=([tabs,"top",50],[tabs,"left",0],[tabs,"bottom",25],[tabs,"right",0]) )
	cmds.formLayout( jpmAW_form, e=1, af=([jpmAW_nameField,"top",0],[jpmAW_nameField,"left",0],[jpmAW_nameField,"right",0]) )
	cmds.formLayout( animFileForm, e=1, af=([animFileList,"top",0],[animFileList,"left",0],[animFileList,"bottom",0],[animFileList,"right",0]) )
	cmds.formLayout( poseFileForm, e=1, af=([poseFileList,"top",0],[poseFileList,"left",0],[poseFileList,"bottom",0],[poseFileList,"right",0]) )
	cmds.formLayout( selFileForm, e=1, af=([selFileList,"top",0],[selFileList,"left",0],[selFileList,"bottom",25],[selFileList,"right",0]) )
	cmds.formLayout( selFileForm, e=1, af=([selRadio,"bottom",0],[selRadio,"left",0],[selRadio,"right",0]) )
	cmds.formLayout( settingsForm, e=1, af=([settingsLayout,"top",0],[settingsLayout,"left",0],[settingsLayout,"bottom",0],[settingsLayout,"right",0] ) )
	cmds.formLayout( jpmAW_form, e=1, af=([applyButton,"left",0],[applyButton,"bottom",0],[applyButton,"right",0]) )

	jpmAW_populateFileList(currentSort)
	
	cmds.showWindow( winName )