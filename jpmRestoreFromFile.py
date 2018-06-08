import maya.cmds as cmds
import maya.mel as mm
import os

import jpmAmIaReference as ref


##stored as
##obj#attr#time#value#inTangentType#outTangentType#inWeight#outWeight#inAngle#outAngle#weightedTangents#lockTangents
##0    1    2     3          4           5             6         7       8      9            10              11
## Sample:  6   187.7153882 clamped    clamped         1         1  80.33105156 80.33105156   0               1 //
##ob::objectName == the object's name
##at::attributeName == the attribute's name
##sv::staticValue == the value of the attribute at the time the file was written
##kv::keyValues == the array of values that make a key
##				kv:t,v,it,ot,iw,ow,ia,oa,wt,lt

def jpmRestoreFromFile(filename, placeTime, placeValue, selectionType, refReTarget):
	##get the data from the file
	linesFromFile = jpReadLines(filename)
	
	##initialize some variables
	currentObject = ""
	currentAttr = ""
	selectionAdd = 0
	selectionToggle = 0
	if refReTarget:
		prefix = ref.jpmAmIaReference( cmds.ls(sl=1)[0] )
		if prefix == "0":
			prefix = ""
	else:
		prefix = ""
	
	##initialize the progress bars
	progress = 0
	curLine = 0
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	cmds.progressWindow( t="Reading Curves", pr=progress, st="Reading: ", min=0, max=100 )
	cmds.progressBar( gMainProgressBar, edit=1, bp=1, st="Reading: " , min=0, max=100 )
	
	##based on selectionType change some variables
	if selectionType == "add":
		selectionAdd = 1
	if selectionType == "toggle":
		selectionToggle = 1
	if selectionType == "replace":
		cmds.select( cl=1 )
		selectionAdd = 1
	if selectionType == "subtract":
		currentSel = cmds.ls(sl=1)
	
	##begin looping through lines from the file
	for line in linesFromFile:
		##progress the progress bars
		progress = ( (float(curLine)/float(len(linesFromFile))) * 100 )
		cmds.progressWindow( edit=1, ii=1, pr=progress, st=("Reading: " + currentObject) )
		cmds.progressBar( gMainProgressBar, edit=1, ii=1, pr=progress, st=("Reading: " + currentObject) )
		curLine = (curLine + 1 )
		
		#initialize some more variables
		partsOfLine = []
		partsOfLine = line.split("::")
		typeOfLine = partsOfLine[0]
		lineData = partsOfLine[1]
		
		##decision tree of what to do with the line based
		##on what kind of line it is
		if typeOfLine == "sl":
			currentObject = lineData
			if refReTarget:
				currentObject = jpmReConstObj(currentObject, prefix)
			cmds.select( currentObject, add=selectionAdd )#, tgl=selectionToggle )
			print "select " + currentObject + " -add " + str(selectionAdd)
		if typeOfLine == "ob":
			currentObject = lineData
			if refReTarget:
				currentObject = jpmReConstObj(currentObject, prefix)
		if typeOfLine == "at":
			currentAttr = lineData
		if typeOfLine == "sv":
			try:
				cmds.setAttr( (currentObject + "." + currentAttr), float(lineData) )
			except RuntimeError:
				print "I think this means that " + currentObject + "." + currentAttr + " is locked or otherwise unsettable"
		if typeOfLine == "kv":
			##split the line data into it's individual components
			keyData = []
			keyData = lineData.split(",")
			
			##split the keyData up into seperate variables of the appropriate type
			keyTime = float( keyData[0] ) + float( placeTime )
			keyValue = float( keyData[1] )
			inTangent = keyData[2]
			outTangent = keyData[3]
			inWeight = float( keyData[4] )
			outWeight = float( keyData[5] )
			inAngle = float( keyData[6] )
			outAngle = float( keyData[7] )
			weightedTangents = float( keyData[8] )
			lockedTangents = float( keyData[9] )
			
			##make the new key and set it's values and attributes
			cmds.select( cl=1 )
			cmds.select( currentObject )
			cmds.setKeyframe( at=currentAttr, v=keyValue, t=keyTime )
			cmds.keyTangent( at=currentAttr, t=(keyTime,keyTime), l=lockedTangents )
			cmds.keyTangent( at=currentAttr, t=(keyTime,keyTime), wt=weightedTangents )
			cmds.keyTangent( at=currentAttr, t=(keyTime,keyTime), itt=inTangent )
			cmds.keyTangent( at=currentAttr, t=(keyTime,keyTime), ott=outTangent )
			cmds.keyTangent( at=currentAttr, t=(keyTime,keyTime), ia=inAngle )
			cmds.keyTangent( at=currentAttr, t=(keyTime,keyTime), oa=outAngle )
			cmds.keyTangent( at=currentAttr, t=(keyTime,keyTime), iw=inWeight )
			cmds.keyTangent( at=currentAttr, t=(keyTime,keyTime), ow=outWeight )
		
		##check to see if the user wants to cancel out
		cancel = cmds.progressBar( gMainProgressBar, q=1, ic=1 )
		if cancel != 0:
			cmds.progressWindow( e=1, ep=1 )
			cmds.progressBar( gMainProgressBar, e=1, ep=1 )
			cancel = 1
			break
			
	##kill the progress bars
	cmds.progressWindow( ep=1 )
	cmds.progressBar( gMainProgressBar, e=1, ep=1 )

##read lines in from a file on disk
def jpReadLines( fileToRead):
	lines = []
	badLines = []

	if os.path.exists(fileToRead) == False:
		print "File Not Found"
	else:
		thisFile = file(fileToRead, "r+")
		badLines = thisFile.readlines()
		thisFile.close()
	for i in range(0, len(badLines)):
		lines.append(badLines[i].strip())
	return lines


def jpmReConstObj(object, prefix):
	reConst = ""
	tokObj=object.split("|")
	if len(tokObj) > 1:
		for level in tokObj:
			reConst = (reConst + prefix + level + "|" )
	else:
		reConst = (prefix + tokObj[len(tokObj)-1])

	return reConst