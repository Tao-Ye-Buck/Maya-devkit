# Copyright 2015 Autodesk, Inc. All rights reserved.
# 
# Use of this software is subject to the terms of the Autodesk
# license agreement provided at the time of installation or download,
# or which otherwise accompanies this software in either electronic
# or hard copy form.

from ctypes import *
import maya.api.OpenMayaRender as omr
import maya.api.OpenMaya as om

# Example plugin: vertexBufferGenerator.py
#
# This plug-in is an example of a custom MPxVertexBufferGenerator.
# It provides custom vertex streams based on shader requirements coming from 
# an MPxShaderOverride.  The semanticName() in the MVertexBufferDescriptor is used 
# to signify a unique identifier for a custom stream.

# This plugin is meant to be used in conjunction with the d3d11Shader or cgShader plugins.

# The vertexBufferGeneratorGL.cgfx and vertexBufferGeneratorDX11.fx files accompanying this sample
# can be loaded using the appropriate shader plugin.
# The Names of the streams and the stream data generated by this plugin match what is 
# expected from the included effects files.
# This sample use the MyCustomBufferGenerator to create a custom made streams.

# The vertexBufferGenerator2GL.cgfx and vertexBufferGenerator2DX11.fx files accompanying this sample
# can be loaded using the appropriate shader plugin.
# The Names of the streams and the stream data generated by this plugin match what is 
# expected from the included effects files.
# This sample use the MyCustomBufferGenerator2 to create a custom made streams
# by combining the Position and Normal streams in a single one.

def maya_useNewAPI():
	"""
	The presence of this function tells Maya that the plugin produces, and
	expects to be passed, objects created using the Maya Python API 2.0.
	"""
	pass


class MyCustomBufferGenerator(omr.MPxVertexBufferGenerator):
	def __init__(self):
		omr.MPxVertexBufferGenerator.__init__(self)

	def getSourceIndexing(self, object, sourceIndexing):
		# get the mesh from the object
		mesh = om.MFnMesh(object)

		# if it is an empty mesh we do nothing.
		numPolys = mesh.numPolygons
		if numPolys == 0:
			return False

		vertToFaceVertIDs = sourceIndexing.indices()
		faceNum = 0

		# for each face
		for i in range(0, numPolys):

			# assign a color ID to all vertices in this face.
			faceColorID = faceNum % 3

			vertexCount = mesh.polygonVertexCount(i)
			for x in range(0, vertexCount):
				# set each face vertex to the face color
				vertToFaceVertIDs.append(faceColorID)

			faceNum += 1

		# assign the source indexing
		sourceIndexing.setComponentType(omr.MComponentDataIndexing.kFaceVertex)

		return False

	def getSourceStreams(self, object, sourceStreams):
		#No source stream needed
		return False

	def createVertexStream(self, object, vertexBuffer, targetIndexing, sharedIndexing, sourceStreams):
		# get the descriptor from the vertex buffer.  
		# It describes the format and layout of the stream.
		descriptor = vertexBuffer.descriptor()
        
		# we are expecting a float stream.
		if descriptor.dataType != omr.MGeometry.kFloat:
			return

		# we are expecting a float2
		if descriptor.dimension != 2:
			return

		# we are expecting a texture channel
		if descriptor.semantic != omr.MGeometry.kTexture:
			return

		# get the mesh from the current path
		# if it is not a mesh we do nothing.
		mesh = om.MFnMesh(object)

		indices = targetIndexing.indices()
			
		vertexCount = len(indices)
		if vertexCount <= 0:
			return

		# fill the data.
		buffer = vertexBuffer.acquire(vertexCount, True)	# writeOnly = True - we don't need the current buffer values

		inc = sizeof(c_float)
		address = buffer

		for i in range(0, vertexCount):
			# Here we are embedding some custom data into the stream.
			# The included effects (vertexBufferGeneratorGL.cgfx and
			# vertexBufferGeneratorDX11.fx) will alternate 
			# red, green, and blue vertex colored triangles based on this input.
			c_float.from_address(address).value = 1.0
			address += inc

			c_float.from_address(address).value = indices[i] # color index
			address += inc

		# commit the buffer to signal completion.
		vertexBuffer.commit(buffer)


class MyCustomBufferGenerator2(omr.MPxVertexBufferGenerator):
	def __init__(self):
		omr.MPxVertexBufferGenerator.__init__(self)

	def getSourceIndexing(self, object, sourceIndexing):
		# get the mesh from the object
		mesh = om.MFnMesh(object)

		(vertexCount, vertexList) = mesh.getVertices()
		vertCount = len(vertexList)

		vertices = sourceIndexing.indices()
		for i in range(0, vertCount):
			vertices.append( vertexList[i] )

		return True

	def getSourceStreams(self, object, sourceStreams):
		sourceStreams.append( "Position" )
		sourceStreams.append( "Normal" )
		return True

	def createVertexStream(self, object, vertexBuffer, targetIndexing, sharedIndexing, sourceStreams):
		# get the descriptor from the vertex buffer.  
		# It describes the format and layout of the stream.
		descriptor = vertexBuffer.descriptor()
        
		# we are expecting a float or int stream.
		dataType = descriptor.dataType
		if dataType != omr.MGeometry.kFloat and dataType != omr.MGeometry.kInt32:
			return

		# we are expecting a dimension of 3 or 4
		dimension = descriptor.dimension
		if dimension != 4 and dimension != 3:
			return

		# we are expecting a texture channel
		if descriptor.semantic != omr.MGeometry.kTexture:
			return

		# get the mesh from the current path
		# if it is not a mesh we do nothing.
		mesh = om.MFnMesh(object)

		indices = targetIndexing.indices()

		vertexCount = len(indices)
		if vertexCount <= 0:
			return

		positionStream = sourceStreams.getBuffer( "Position" )
		if positionStream == None or positionStream.descriptor().dataType != omr.MGeometry.kFloat:
			return
		positionDimension = positionStream.descriptor().dimension
		if positionDimension != 3 and positionDimension != 4:
			return

		normalStream = sourceStreams.getBuffer( "Normal" )
		if normalStream == None or normalStream.descriptor().dataType != omr.MGeometry.kFloat:
			return
		normalDimension = normalStream.descriptor().dimension
		if normalDimension != 3 and normalDimension != 4:
			return

		positionBuffer = positionStream.map()
		if positionBuffer != 0:
			normalBuffer = normalStream.map()
			if normalBuffer != 0:
				compositeBuffer = vertexBuffer.acquire(vertexCount, True) # writeOnly = True - we don't need the current buffer values
				if compositeBuffer != 0:

					compaddress = compositeBuffer
					posaddress = positionBuffer
					normaddress = normalBuffer

					floatinc = sizeof(c_float)
					intinc = sizeof(c_int)

					if dataType == omr.MGeometry.kFloat:

						for i in range(0, vertexCount):
							xcompaddr = compaddress
							ycompaddr = compaddress+floatinc
							zcompaddr = compaddress+2*floatinc
							wcompaddr = compaddress+3*floatinc

							#xposaddr = posaddress
							yposaddr = posaddress+floatinc
							zposaddr = posaddress+2*floatinc

							xnormaddr = normaddress
							#ynormaddr = normaddress+floatinc
							znormaddr = normaddress+2*floatinc

							c_float.from_address(xcompaddr).value = c_float.from_address(yposaddr).value  # store position.y
							c_float.from_address(ycompaddr).value = c_float.from_address(zposaddr).value  # store position.z
							c_float.from_address(zcompaddr).value = c_float.from_address(xnormaddr).value # store normal.x
							if dimension == 4:
								c_float.from_address(wcompaddr).value = c_float.from_address(znormaddr).value # store normal.z

							compaddress += dimension*floatinc
							posaddress += positionDimension*floatinc
							normaddress += normalDimension*floatinc

					elif dataType == omr.MGeometry.kInt32:

						for i in range(0, vertexCount):
							xcompaddr = compaddress
							ycompaddr = compaddress+intinc
							zcompaddr = compaddress+2*intinc
							wcompaddr = compaddress+3*intinc

							#xposaddr = posaddress
							yposaddr = posaddress+floatinc
							zposaddr = posaddress+2*floatinc

							xnormaddr = normaddress
							#ynormaddr = normaddress+floatinc
							znormaddr = normaddress+2*floatinc

							c_int.from_address(xcompaddr).value = c_float.from_address(yposaddr).value * 255  # store position.y
							c_int.from_address(ycompaddr).value = c_float.from_address(zposaddr).value * 255  # store position.z
							c_int.from_address(zcompaddr).value = c_float.from_address(xnormaddr).value * 255 # store normal.x
							if dimension == 4:
								c_int.from_address(wcompaddr).value = c_float.from_address(znormaddr).value * 255 # store normal.z

							compaddress += dimension*intinc
							posaddress += positionDimension*floatinc
							normaddress += normalDimension*floatinc
					
					vertexBuffer.commit(compositeBuffer)

				normalStream.unmap()

			positionStream.unmap()

# This is the buffer generator creation function registered with the DrawRegistry.
# Used to initialize the generator.
def createMyCustomBufferGenerator():
	return MyCustomBufferGenerator()

def createMyCustomBufferGenerator2():
	return MyCustomBufferGenerator2()

# The following routines are used to register/unregister
# the vertex generators with Maya

def initializePlugin(obj):

	# register a generator based on a custom semantic for DX11.  You can use any name in DX11.
	omr.MDrawRegistry.registerVertexBufferGenerator("myCustomStream", createMyCustomBufferGenerator)

	# register a generator based on a custom semantic for cg.  
	# Pretty limited in cg so we hook onto the "ATTR" semantics.
	omr.MDrawRegistry.registerVertexBufferGenerator("ATTR8", createMyCustomBufferGenerator)


	# register a generator based on a custom semantic for DX11.  You can use any name in DX11.
	omr.MDrawRegistry.registerVertexBufferGenerator("myCustomStreamB", createMyCustomBufferGenerator2)

	# register a generator based on a custom semantic for cg.  
	# Pretty limited in cg so we hook onto the "ATTR" semantics.
	omr.MDrawRegistry.registerVertexBufferGenerator("ATTR7", createMyCustomBufferGenerator2)

def uninitializePlugin(obj):

	omr.MDrawRegistry.deregisterVertexBufferGenerator("myCustomStream")

	omr.MDrawRegistry.deregisterVertexBufferGenerator("ATTR8")

	omr.MDrawRegistry.deregisterVertexBufferGenerator("myCustomStreamB")

	omr.MDrawRegistry.deregisterVertexBufferGenerator("ATTR7")

