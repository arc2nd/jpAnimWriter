##James Parks  060205
##jpmAmIaReference.mel

##This script determines whether a selected object is referenced from a file.
##Then it goes and finds whether it was referenced with namespaces or with prefixes.
##If referenced with namespaces the namespace is returned.
##If referenced with prefixes the prefix is then found and returned.


import maya.cmds as cmds
import re

##jpmAmIaReference("tmp:WORLD")
##selected = "tmp:WORLD"

def jpmAmIaReference(selected):
	verboseLevel = 0
	if selected == "":
		return "0"
	try:
		refTest = cmds.referenceQuery( selected, f=1 )
	except:
		refTest = 0
		
	if refTest != 0:
		###################
		##Find the filename
		###################
		refFile = cmds.referenceQuery( selected, f=1 )
		tokRefFile = re.split( "/", refFile )
		
		###################
		##Is it a namespace? Split for ":" in the namespace
		###################
		refNodes = cmds.referenceQuery( refFile, n=1 )
		tokNameSpace = re.split( ":", refNodes[0] )
		NS_tokens = len( tokNameSpace )
		
		##No matter how deep it's referenced this should get them all,... I hope
		finalNS = ""
		for i in range(0, (NS_tokens-1) ):
			finalNS = (finalNS + tokNameSpace[i] + ":")
		
		###################
		##Find the Prefix by comparing the first and last node names starting from the front
		###################
		prefix = ""
		firstNodeSize = len(refNodes[0])
		
		for i in range( 0, firstNodeSize ):
			refSize = len(refNodes)
			subStringOne = refNodes[0][0:i]
			subStringTwo = refNodes[(refSize-1)][0:i]
			if verboseLevel != 0:
				print (subStringOne + " || " + subStringTwo + "\n")
			if subStringOne == subStringTwo:
				prefix = refNodes[0][0:i]

		###################
		##Return the appropriate response
		###################
		if NS_tokens > 1:
			print ("I am a reference. My name space is " + finalNS)
			return finalNS
		elif prefix != "":
			print ("I am a reference. My prefix is " + prefix)
			return prefix
		else:
			print "I am _NOT_ a reference"
			return "0"
	else:
		print "I am _NOT_ a reference"
		return "0"