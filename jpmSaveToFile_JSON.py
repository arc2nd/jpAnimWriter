import maya.cmds as cmds
import maya.mel as mm
import re
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


def jpmSaveAnimationToFile(name, min, max, saveType, selected, keyableAttrs, refReTarget=False):
	"""Save an animation to a JSON formated file"""
	##initialize some variables
	reCreateKeyableAttrs = True
	verboseLevel = False
	cancel = False
	
	##sanity check to see if anything is selected
	numOfAnimObjs = float(len(selected))
	if numOfAnimObjs <=0:
		cmds.error("Nothing is currently selected. No File created or action taken.")
		return
		
	##initialize the progress bars
	progress = 0
	curNumObj = 1
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	cmds.progressWindow(t="Writing Curves", pr=progress, st="Writing: ", min=0, max=100)
	cmds.progressBar(gMainProgressBar, edit=1, bp=1, st="Writing: ", min=0, max=100)
	
	##begin looping through objects
	safeFileDict = {}
	for object in selected:
		##sanitize the object name for references
		#strippedObj = jpmHandleReference_write(object)
		prefix = ref.jpmAmIaReference(object)
		if refReTarget:
			strippedObj = jpmDeConstObj(object, prefix)
		else:
			strippedObj = object
		
		
		##progress the progress bars
		progress = ((float(curNumObj)/float(numOfAnimObjs)) * 100)
		cmds.progressWindow(edit=1, ii=1, pr=progress, st=("Writing: " + strippedObj))
		cmds.progressBar(gMainProgressBar, edit=1, ii=1, pr=progress, st=("Writing: " + strippedObj))
		curNumObj = (curNumObj + 1)
	
		##find out what attributes are keyable
		if keyableAttrs[0] == "" or reCreateKeyableAttrs == 1:
			keyableAttrs = cmds.listAttr(strippedObj, r=1, w=1, k=1, u=1, v=1, m=1, s=1)
			reCreateKeyableAttrs = 1
		##begin looping through attributes
		attrDict = {}
		for attr in keyableAttrs:
			##print attr
			##get the current attribute value
			staticValue = cmds.getAttr( strippedObj + "." + attr )
						
			##get the number of keys in the curve
			cmds.selectKey( clear=1 )
			numOfKeys = cmds.selectKey( (strippedObj + "." + attr), add=1, k=1, t=(min,max) )
			keyIndices = []
			keyIndices = cmds.keyframe( q=1, sl=1, iv=1 ) 
			
			if keyIndices > 0:
				##begin looping through all the keys on this animation curve
				try:
					valuesDict = {}
					for key in keyIndices:
						##print key
						keyValueArray = jpmGetInfoOnAKey(strippedObj, attr, key)
						valuesDict[key] = keyValueArray
				except TypeError:
					print (strippedObj + "." + attr + " is not keyed")
				attrDict[attr] = valuesDict
			elif not keyIndices > 0:
				attrDict[attr] = staticValue
		safeFileDict[strippedObj] = attrDict
		
		##check to see if the user wants to cancel out
		cancel = cmds.progressBar(gMainProgressBar, q=1, ic=1)
		if cancel != 0:
			cmds.progressWindow(e=1, ep=1)
			cmds.progressBar(gMainProgressBar, e=1, ep=1)
			cancel = 1
			break
	safeFileDict["AWFileType"] = "anim"
			
	##actually write the file out
	saveFile = open(name,'w')
	json.dump(safeFileDict,saveFile,indent=4, sort_keys=True)
	saveFile.close()
	
	cmds.progressWindow(ep=1)
	cmds.progressBar(gMainProgressBar, e=1, ep=1)
	
	

def jpmSavePoseToFile(name, saveType, selected, keyableAttrs, refReTarget=True):
	"""Save a pose to a JSON formated file"""
	##initialize some variables
	reCreateKeyableAttrs = True
	verboseLevel = False
	cancel = False
	
	##sanity check to see if anything is selected
	numOfAnimObjs = float(len(selected))
	if numOfAnimObjs <=0:
		cmds.error("Nothing is currently selected. No File created or action taken.")
		return
		
	##initialize the progress bars
	progress = 0
	curNumObj = 1
	gMainProgressBar = mm.eval('$tmp = $gMainProgressBar')
	cmds.progressWindow(t="Writing Curves", pr=progress, st="Writing: ", min=0, max=100)
	cmds.progressBar(gMainProgressBar, edit=1, bp=1, st="Writing: ", min=0, max=100)
	
	##begin looping through objects
	safeFileDict = {}
	
	##begin looping through objects
	safeFileDict = {}
	for object in selected:
		##sanitize the object name for references
		#strippedObj = jpmHandleReference_write(object)
		prefix = ref.jpmAmIaReference(object)
		if refReTarget:
			strippedObj = jpmDeConstObj(object, prefix)
		else:
			strippedObj = object
		
		
		##progress the progress bars
		progress = ((float(curNumObj)/float(numOfAnimObjs)) * 100)
		cmds.progressWindow(edit=1, ii=1, pr=progress, st=("Writing: " + strippedObj))
		cmds.progressBar(gMainProgressBar, edit=1, ii=1, pr=progress, st=("Writing: " + strippedObj))
		curNumObj = (curNumObj + 1)
	
		##find out what attributes are keyable
		if keyableAttrs[0] == "" or reCreateKeyableAttrs == 1:
			keyableAttrs = cmds.listAttr(strippedObj, r=1, w=1, k=1, u=1, v=1, m=1, s=1)
			reCreateKeyableAttrs = 1
		##begin looping through attributes
		attrDict = {}
		for attr in keyableAttrs:
			##print attr
			##get the current attribute value
			staticValue = cmds.getAttr(strippedObj + "." + attr)
			attrDict[attr] = staticValue
		safeFileDict[strippedObj] = attrDict

		##check to see if the user wants to cancel out
		cancel = cmds.progressBar( gMainProgressBar, q=1, ic=1 )
		if cancel != 0:
			cmds.progressWindow( e=1, ep=1 )
			cmds.progressBar( gMainProgressBar, e=1, ep=1 )
			cancel = 1
			break

	safeFileDict["AWFileType"] = "pose"
		
	##actually write the file out
	saveFile = open(name,'w')
	json.dump(safeFileDict,saveFile,indent=4, sort_keys=True)
	saveFile.close()
	
	cmds.progressWindow(ep=1)
	cmds.progressBar(gMainProgressBar, e=1, ep=1)
			
def jpmSavePoseToFile_OLD(name, selected=[], keyableAttrs=[], refReTarget=0):
	##initialize some variables
	verboseLevel = 0
	cancel = 0
	safeFileCommand = ""
	reCreateKeyableAttrs = 1
	
	##sanity check to see if anything is selected
	numOfObjs = len(selected)
	if numOfObjs <= 0:
		mm.error( "Nothing is currently selected. No file created or action taken." )
		
	##begin looping through objects
	safeFileDict = {}
	for object in selected:
		prefix = ref.jpmAmIaReference( object )
		if refReTarget:
			strippedObj = jpmDeConstObj( object, prefix )
		else:
			strippedObj = object
		safeFileCommand = (safeFileCommand + "ob::" + strippedObj + "\n")
		if keyableAttrs[0] == "" or reCreateKeyableAttrs == 1:
			keyableAttrs = cmds.listAttr( object, r=1, w=1, k=1, u=1, v=1, m=1, s=1 )
			reCreateKeyableAttrs = 1
		##begin looping through attributes
		for attr in keyableAttrs:
			safeFileCommand = (safeFileCommand + "at::" + attr + "\n")
			staticValue = cmds.getAttr( object + "." + attr )
			safeFileCommand = (safeFileCommand + "sv::" + str(staticValue) + "\n")
	
	safeFileDict["AWFileType"] = "sel"

	##actually write the file out
	saveFile = file(name, "w+")
	saveFile.write(safeFileCommand)
	saveFile.close()
			
def jpmSaveSelectionToFile(name, selected=[], refReTarget=0):
	##initialize some variables
	verboseLevel = 0
	cancel = 0
	safeFileCommand = ""
	
	##sanity check to see if anything is selected
#	numOfObjs = len(selected)
	#if numOfObjs <= 0:
	#	mm.error( "Nothing is currently selected. No file created or action taken." )
	
	##begin looping through objects
	for object in selected:
		prefix = ref.jpmAmIaReference( object )
		if refReTarget:
			strippedObj = jpmDeConstObj( object, prefix )
		else:
			strippedObj = object
		safeFileCommand = (safeFileCommand + "sl::" + strippedObj + "\n")
		
	##actually write the file out
	saveFile = file(name, "w+")
	saveFile.write(safeFileCommand)
	saveFile.close()

##############################
##Collect information on a specified key
##############################
##must be called like:
##keyIndices = cmds.keyframe( q=1, sl=1, iv=1 )
##keyData = jpGetInfoOnAKey("duck_RIG:head_CTRL", "rotateX", (keyIndices[0],keyIndices[0]) )

def jpmGetInfoOnAKey(obj, attr, keyIndex):
	keyTime_FL = cmds.keyframe( obj, index=(keyIndex,keyIndex), q=1, tc=1, at=attr)
	keyValue_FL = cmds.keyframe( obj, index=(keyIndex,keyIndex), q=1, vc=1, at=attr) 
	inTangentType = cmds.keyTangent( obj, index=(keyIndex,keyIndex), q=1, itt=1, at=attr) 
	outTangentType = cmds.keyTangent( obj, index=(keyIndex,keyIndex), q=1, ott=1, at=attr) 
	inWeight_FL = cmds.keyTangent( obj, index=(keyIndex,keyIndex), q=1, iw=1, at=attr) 
	outWeight_FL = cmds.keyTangent( obj, index=(keyIndex,keyIndex), q=1, ow=1, at=attr) 
	inAngle_FL = cmds.keyTangent( obj, index=(keyIndex,keyIndex), q=1, ia=1, at=attr) 
	outAngle_FL = cmds.keyTangent( obj, index=(keyIndex,keyIndex), q=1, oa=1, at=attr) 
	weightedTangents_FL = cmds.keyTangent( obj, index=(keyIndex,keyIndex), q=1, wt=1, at=attr) 
	lockTangents_FL = cmds.keyTangent( obj, index=(keyIndex,keyIndex), q=1, l=1, at=attr) 

	if inTangentType == "fixed" or outTangentType == "fixed":
		inWeight_FL = 1.0
		outWeight_FL = 1.0
		inAngle_FL = 0.0
		outAngle_FL = 0.0
		weightedTangents_FL = 0.0
		lockTangents_FL = 1.0
	
	##make all collected values strings
	keyTime = str(keyTime_FL[0])
	keyValue = str(keyValue_FL[0])
	inWeight = str(inWeight_FL[0])
	outWeight = str(outWeight_FL[0])
	inAngle = str(inAngle_FL[0])
	outAngle = str(outAngle_FL[0])
	weightedTangents = str(weightedTangents_FL[0])
	lockTangents = str(lockTangents_FL[0])

	keyInfo = [keyTime, keyValue, inTangentType[0], outTangentType[0], inWeight, outWeight, inAngle, outAngle, weightedTangents, lockTangents]

	return keyInfo

def jpmDeConstObj(object, prefix):
	deConst = ""
	tokObj = object.split("|")
	for obj in tokObj:
		deConst = deConst + obj.split(":")[-1] + "|"
	return deConst[:-1]