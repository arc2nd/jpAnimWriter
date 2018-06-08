import maya.cmds as cmds
import maya.mel as mm
import os
import json

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
	thisFile = open(filename, "r")
	dataDict = json.load(thisFile)
	thisFile.close()
	
	##initialize some variables
	currentObject = ""
	currentAttr = ""
	selectionAdd = 0
	selectionToggle = 0
	if refReTarget:
		prefix = ref.jpmAmIaReference(cmds.ls(sl=1)[0])
		if prefix == "0":
			prefix = ""
	else:
		prefix = ""
	
	##initialize the progress bars
	progress = 0
	curLine = 0
	objectsInFile = len(dataDict.keys()) - 1
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	cmds.progressWindow(t="Reading Curves", pr=progress, st="Reading: ", min=0, max=100)
	cmds.progressBar(gMainProgressBar, edit=1, bp=1, st="Reading: " , min=0, max=100)
	
	##based on selectionType change some variables
	if selectionType == "add":
		selectionAdd = 1
	if selectionType == "toggle":
		selectionToggle = 1
	if selectionType == "replace":
		cmds.select(cl=1)
		selectionAdd = 1
	if selectionType == "subtract":
		currentSel = cmds.ls(sl=1)
		
	AWFileType = dataDict["AWFileType"]
	
	if AWFileType == "anim" or AWFileType == "pose":
		for object in dataDict.keys():
			if object == "AWFileType":
					pass
					
			##progress the progress bars
			progress = ((float(curLine)/float(objectsInFile)) * 100)
			cmds.progressWindow(edit=1, ii=1, pr=progress, st=("Reading: " + object))
			cmds.progressBar(gMainProgressBar, edit=1, ii=1, pr=progress, st=("Reading: " + object))
			curLine = (curLine + 1)

			##If reference retargeting is on, build the reconstructed object name
			if refReTarget:
				#prefix = ref.jpmAmIaReference(object)
				reConstObj = jpmReConstObj(object, prefix)
			else:
				reConstObj = object
			
			if type(dataDict[object]) == type({}):
				for attribute in dataDict[object].keys():
					if type(dataDict[object][attribute]) == type({}):
						#Is an animated value
						for keyIndex in dataDict[object][attribute].keys():
							keyValueArray = dataDict[object][attribute][keyIndex]
							rebuildKey(object, attribute, keyValueArray, placeTime, placeValue)
					else:
						#Is a static value
						value = dataDict[object][attribute]
						if cmds.objExists(reConstObj):
							if cmds.attributeQuery(attribute, exists=True, node=object):
								cmds.setAttr(object + "." + attribute, value)
								
					##check to see if the user wants to cancel out
					cancel = cmds.progressBar(gMainProgressBar, q=1, ic=1)
					if cancel != 0:
						cmds.progressWindow(e=1, ep=1)
						cmds.progressBar(gMainProgressBar, e=1, ep=1)
						cancel = 1
						break

	elif AWFileType == "sel":
		savedList = []
		for object in dataDict.keys():
			if object == "AWFileType":
				pass
			else:
				savedList.append(object)
				
		if selectionType == "add":
			cmds.select(savedList, add=True)
		elif selectionType == "toggle":
			newList = []
			currentSelection = cmds.ls(sl=True)
			cmds.select(newList)
		elif selectionType == "replace":
			cmds.select(clear=True)
			cmds.select(savedList)
		elif selectionType == "subtract":
			newList = []
			currentSelection = cmds.ls(sl=True)
			cmds.select(newList)
		else:
			print "Don't know the selection type"
				
	##kill the progress bars
	cmds.progressWindow(ep=1)
	cmds.progressBar(gMainProgressBar, e=1, ep=1)
			
def rebuildKey(object, attribute, keyData, placeTime, placeValue):
	##split the keyData up into seperate variables of the appropriate type
	keyTime = float(keyData[0]) + float(placeTime)
	keyValue = float(keyData[1])
	inTangent = keyData[2]
	outTangent = keyData[3]
	inWeight = float(keyData[4])
	outWeight = float(keyData[5])
	inAngle = float(keyData[6])
	outAngle = float(keyData[7])
	if keyData[8]:
		weightedTangents = 1
	else:
		weightedTangents = 0
	#weightedTangents = keyData[8]
	if keyData[9]:
		lockedTangents = 1
	else:
		lockedTangents = 0
	#lockedTangents = int(keyData[9])
	
	##make the new key and set it's values and attributes
	cmds.select(cl=1)
	cmds.select(object)
	cmds.setKeyframe(at=attribute, v=keyValue, t=keyTime)
	cmds.keyTangent(at=attribute, t=(keyTime,keyTime), l=lockedTangents)
	cmds.keyTangent(at=attribute, t=(keyTime,keyTime), wt=weightedTangents)
	cmds.keyTangent(at=attribute, t=(keyTime,keyTime), itt=inTangent )
	cmds.keyTangent(at=attribute, t=(keyTime,keyTime), ott=outTangent)
	cmds.keyTangent(at=attribute, t=(keyTime,keyTime), ia=inAngle)
	cmds.keyTangent(at=attribute, t=(keyTime,keyTime), oa=outAngle)
	cmds.keyTangent(at=attribute, t=(keyTime,keyTime), iw=inWeight)
	cmds.keyTangent(at=attribute, t=(keyTime,keyTime), ow=outWeight)

def jpmReConstObj(object, prefix):
	reConst = ""
	tokObj=object.split("|")
	if len(tokObj) > 1:
		for level in tokObj:
			reConst = (reConst + prefix + level + "|")
	else:
		reConst = (prefix + tokObj[len(tokObj)-1])

	return reConst

