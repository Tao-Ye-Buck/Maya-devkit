#-
# ==========================================================================
# Copyright (C) 1995 - 2006 Autodesk, Inc. and/or its licensors.  All 
# rights reserved.
#
# The coded instructions, statements, computer programs, and/or related 
# material (collectively the "Data") in these files contain unpublished 
# information proprietary to Autodesk, Inc. ("Autodesk") and/or its 
# licensors, which is protected by U.S. and Canadian federal copyright 
# law and by international treaties.
#
# The Data is provided for use exclusively by You. You have the right 
# to use, modify, and incorporate this Data into other products for 
# purposes authorized by the Autodesk software license agreement, 
# without fee.
#
# The copyright notices in the Software and this entire statement, 
# including the above license grant, this restriction and the 
# following disclaimer, must be included in all copies of the 
# Software, in whole or in part, and all derivative works of 
# the Software, unless such copies or derivative works are solely 
# in the form of machine-executable object code generated by a 
# source language processor.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. 
# AUTODESK DOES NOT MAKE AND HEREBY DISCLAIMS ANY EXPRESS OR IMPLIED 
# WARRANTIES INCLUDING, BUT NOT LIMITED TO, THE WARRANTIES OF 
# NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A PARTICULAR 
# PURPOSE, OR ARISING FROM A COURSE OF DEALING, USAGE, OR 
# TRADE PRACTICE. IN NO EVENT WILL AUTODESK AND/OR ITS LICENSORS 
# BE LIABLE FOR ANY LOST REVENUES, DATA, OR PROFITS, OR SPECIAL, 
# DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES, EVEN IF AUTODESK 
# AND/OR ITS LICENSORS HAS BEEN ADVISED OF THE POSSIBILITY 
# OR PROBABILITY OF SUCH DAMAGES.
#
# ==========================================================================
#+

# import maya.cmds
# maya.cmds.loadPlugin("blindDoubleDataCmd.py")
# maya.cmds.sphere()
# maya.cmds.spBlindDoubleData()

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginName = "spBlindDoubleData"
kPluginDataId = OpenMaya.MTypeId(0x87011)

#
fValueDictionary={}

# testing function
def printMsg(msg):
	print msg
	stream=OpenMaya.MStreamUtils.stdOutStream()
	OpenMaya.MStreamUtils.writeCharBuffer(stream,msg)

# data
class blindDoubleData(OpenMayaMPx.MPxData):
	def __init__(self):
		OpenMayaMPx.MPxData.__init__(self)
		self.__fValue = 0.0
		fValueDictionary[OpenMayaMPx.asHashable(self)]=self.__fValue

	def readASCII(self, args, lastParsedElement):
		try:
			if args.length() > 0:
				parsedIndex = OpenMaya.MScriptUtil.getUint(lastParsedElement)
				self.__fValue = args.asDouble( parsedIndex )
				parsedIndex += 1
				OpenMaya.MScriptUtil.setUint(lastParsedElement,parsedIndex)
				fValueDictionary[OpenMayaMPx.asHashable(self)]=self.__fValue
		except:
			sys.stderr.write("Failed to read ASCII value.")
			raise

	def readBinary(self, inStream, length):
		readParam = OpenMaya.MScriptUtil(0.0)
		readPtr = readParam.asDoublePtr()
		OpenMaya.MStreamUtils.readDouble(inStream, readPtr, True )
		self.__fValue = readParam.getDouble(readPtr)

	def writeASCII(self, out):
		try:
			OpenMaya.MStreamUtils.writeDouble(out, self.__fValue, False)
		except:
			sys.stderr.write("Failed to write ASCII value.")
			raise

	def writeBinary(self, out):
		try:
			OpenMaya.MStreamUtils.writeDouble(out, self.__fValue, True)
		except:
			sys.stderr.write("Failed to write binary value.")
			raise

	def copy(self, other):
		# Cannot convert other to self.  Use a dictionary
		# to hold the information we need.
		self.__fValue = fValueDictionary[OpenMayaMPx.asHashable(other)]

	def typeId(self):
		return kPluginDataId

	def name(self):
		return kPluginName

	def value(self):
		return self.__fValue

	def setValue(self, newVal):
		self.__fValue = newVal

# command
class blindDoubleDataCmd(OpenMayaMPx.MPxCommand):
	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)
		self.__iter = None

	def doIt(self, args):
		selList = OpenMaya.MSelectionList()
		OpenMaya.MGlobal.getActiveSelectionList(selList)
		self.__iter = OpenMaya.MItSelectionList(selList)
		self.redoIt()

	def redoIt(self):
		dependNode = OpenMaya.MObject() # Selected dependency node
		# show message and advance iterator
		def error(msg):
			sys.stderr.write(err)
			self.__iter.next()
			
		# Iterate over all selected dependency nodes
		#
		while not self.__iter.isDone():
			# Get the selected dependency node and create
			# a function set for it
			#
			try:
				self.__iter.getDependNode(dependNode)	
			except:
				error("Error getting the dependency node")
				continue

			try:
				fnDN = OpenMaya.MFnDependencyNode(dependNode)
			except:
				error("Error creating MFnDependencyNode")
				continue

			# Create a new attribute for our blind data
			#
			fnAttr = OpenMaya.MFnTypedAttribute()
			newAttr = fnAttr.create("blindDoubleData", "BDD", kPluginDataId)
			
			# Now add the new attribute to the current dependency node
			#
			fnDN.addAttribute(newAttr, OpenMaya.MFnDependencyNode.kLocalDynamicAttr)

			# Create a plug to set and retrive value off the node.
			#
			plug = OpenMaya.MPlug(dependNode, newAttr)

			# Instantiate blindDoubleData and set its value.
			#
			newData = OpenMayaMPx.asMPxPtr(blindDoubleData())
			newData.setValue(3.2)

			# Set the value for the plug.
			#
			plug.setMPxData(newData)

			# Now try to retrieve the value off the plug as an MObject.
			#
			try:
				sData = plug.asMObject()
			except:
				error("Error getting value off plug")
				continue
				
			# Convert the data back to MPxData.
			#
			pdFn = OpenMaya.MFnPluginData(sData)
			data = pdFn.constData()

			# Get the value.
			#
			if not data:
				error("Error: failed to retrieve data.")
				continue
				
			self.__iter.next()

	def undoIt(self):
		pass

	def isUndoable(self):
		return True


########################################################################


# Creators
def cmdCreator():
	return OpenMayaMPx.asMPxPtr(blindDoubleDataCmd())

def dataCreator():
	return OpenMayaMPx.asMPxPtr(blindDoubleData())

# Initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject, "Autodesk", "1.0", "Any")
	try:
		mplugin.registerData(kPluginName, kPluginDataId, dataCreator)
	except:
		sys.stderr.write("Failed to register new data type: %s\n" % kPluginName)
		raise
		
	try:
		mplugin.registerCommand(kPluginName, cmdCreator)
	except:
		sys.stderr.write("Failed to register command: %s\n" % kPluginName)
		raise


# Uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterCommand(kPluginName)
	except:
		sys.stderr.write("Failed to unregister command: %s\n" % kPluginName)
		raise

	try:
		mplugin.deregisterData(kPluginDataId)
	except:
		sys.stderr.write("Failed to unregister data type: %s\n" % kPluginName)
		raise

