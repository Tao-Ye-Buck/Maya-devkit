#ifndef _MPxSubSceneOverride
#define _MPxSubSceneOverride
//-
// ===========================================================================
// Copyright 2015 Autodesk, Inc.  All rights reserved.
//
// Use of this software is subject to the terms of the Autodesk license
// agreement provided at the time of installation or download, or which
// otherwise accompanies this software in either electronic or hard copy form.
// ===========================================================================
//+
#if defined __cplusplus

// ****************************************************************************
// INCLUDED HEADER FILES
#include <maya/MObject.h>
#include <maya/MStatus.h>
#include <maya/MBoundingBox.h>
#include <maya/MHWGeometry.h>
#include <maya/MViewport2Renderer.h>
#include <maya/MMatrixArray.h>
#include <maya/MFloatArray.h>

// ****************************************************************************
// NAMESPACE
namespace MHWRender
{

class MSelectionContext;

// ****************************************************************************
// CLASS DECLARATION (MSubSceneContainer)
//! \ingroup OpenMayaRender
//! \brief Container for render items generated by MPxSubSceneOverride
/*!
An instance of this class is associated with each instance of
MPxSubSceneOverride and is used to manage and store the set of render items
required by the override to draw its associated DAG object.

The container is optimized to be used with large numbers of render items.

The container will assume ownership of any render item added to it.
Implementations of MPxSubSceneOverride are free to maintain separate pointers
to render items stored in the container, but those pointers will become invalid
as soon as the associated render item is removed from the container.
*/
class OPENMAYARENDER_EXPORT MSubSceneContainer
{
public:
	bool add(MRenderItem* item);
	bool remove(const MString& name);
	void clear();
	MRenderItem* find(const MString& name);

	unsigned int count() const;
	const MRenderItem* find(const MString& name) const;

	class OPENMAYARENDER_EXPORT Iterator
	{
	public:
		void destroy();
		void reset();
		MRenderItem* next();

	protected:
		friend class MSubSceneContainer;
		Iterator(const void* data, void* iData);
		~Iterator();
		Iterator& operator=(const Iterator&) { return *this; }

	private:
		const void* fData;
		void* fIData;
	};

	class OPENMAYARENDER_EXPORT ConstIterator
	{
	public:
		void destroy();
		void reset();
		const MRenderItem* next();

	protected:
		friend class MSubSceneContainer;
		ConstIterator(const void* data, void* iData);
		~ConstIterator();
		ConstIterator& operator=(const ConstIterator&) { return *this; }

	private:
		const void* fData;
		void* fIData;
	};

	Iterator* getIterator();
	ConstIterator* getConstIterator() const;

	static const char* className();

private:
	MSubSceneContainer(void* classification);
	~MSubSceneContainer();
	MSubSceneContainer(const MSubSceneContainer&) {}
	MSubSceneContainer& operator=(const MSubSceneContainer&) { return *this; }
	void setData(void* data);
	MRenderItem* getMItem(void* id) const;
	void clearCache();
    void postUpdate();

	void* fData;
	void* fItemCache;
	void* fNodeClassification;
};

// ****************************************************************************
// CLASS DECLARATION (MPxSubSceneOverride)
//! \ingroup OpenMayaRender MPx
//! \brief Base class for Viewport 2.0 drawing of DAG nodes which represent sub-scenes
/*!
MPxSubSceneOverride allows the user to completely define the renderable units
(render items) needed to draw a specific DAG object type in Maya when using
Viewport 2.0.

This class is independent of any specific hardware draw API. Implementations
operate using the MRenderItem interface and provide a list of the render items
needed to draw all instances of the associated DAG object. One implementation
of the override will be created for each object in the Maya scene whose
classification string satisfies the classification string used when registering
the override. If the associated DAG object is instanced, the override is
responsible for drawing all instances.

The collection of render items is stored in an MSubSceneContainer object. This
container is suitable for storing and accessing large numbers of render items
(thousands or tens of thousands) in a high performance manner. Implementations
are responsible for assigning a shader and an optional matrix to each render
item and must also provide the geometry for each render item as required by its
shader. Geometry may be shared between render items and management of the
geometry is up to the implementation.

MPxSubSceneOverride falls in between MPxDrawOverride and MPxGeometryOverride
with respect to the amount of control given to the implementation.
MPxDrawOverride allows full control over the entire draw of the object, but as
a result the implementation is entirely responsible for the draw.
MPxGeometryOverride is relatively simple to work with but as a result only
limited control of the draw is available. MPxSubSceneOverride is allowed to
fully define all render items, geometry and shaders providing a high degree of
control. However this definition is abstracted from the hardware draw API so
only one implementation is needed to get support for both DirectX and OpenGL.
Furthermore, Maya will handle actually drawing the render items and thus the
items can participate fully in the Maya rendering pipeline (including
screen-space effects like SSAO, transparency sorting, shadow casting/receiving,
etc.). Finally, render items may specify which draw modes they should draw in
(wireframe, shaded, textured, bounding box) so there is no need for the
implementation to track these modes manually.

MPxSubSceneOverride can be used to provide Viewport 2.0 support for any type of
DAG object, however it is optimized for use in cases where a single DAG object
needs to produce a large number of renderables which are not necessarily
located at the same point in space. For example, this interface would be a good
choice for implementing support for a custom node that needs to read and draw a
full scene based on a description from a cache file.

MPxSubSceneOverride has three stages. In each stage, an instance of MFrameContext
is provided to give some information about the current state of the renderer.
The implementation is also free to query any information it needs from Maya.

1) requiresUpdate() : In this call, the implementation is given constant access
to the set of render items for the object. On the first call it will be empty.
If the method returns true, Maya will call update() and the implementation will
be given the opportunity to add/remove render items from the set as well as to
modify those items. Render item state is maintained as long as the render item
is stored in the MSubSceneContainer object. Thus, if nothing needs to be changed
this method may return false to skip the update phase.

2) update() : In this call, the implementation may add/remove render items
to/from the set, and it may modify existing render items. For each render item
the implementation is required to call setGeometryForRenderItem() to provide
the geometry for the render item. Render items without geometry will not draw.

3) addUIDrawables() : In this call, the implementation may
use MUIDrawManager to draw simple UI shapes like lines, circles, text, etc.
If areUIDrawablesDirty() method returns true, the UI drawables would
be cleared and re-added every refresh. If the dirty is false, the UI drawables
are being persistently kept until either the DAG object associated with
the override is destroyed or the override is deregistered. Note that the UI drawables
don't support instancing draw.

If at the end of these three stages further update is required then
furtherUpdateRequired() can be overridden to indicate whether the three stages
need to be called again. 

Implementations of MPxSubSceneOverride must be registered with Maya through
MDrawRegistry.
*/
class OPENMAYARENDER_EXPORT MPxSubSceneOverride
{
public:
	MPxSubSceneOverride(const MObject& obj);
	virtual ~MPxSubSceneOverride();

	virtual MHWRender::DrawAPI supportedDrawAPIs() const;
	virtual bool requiresUpdate(
		const MSubSceneContainer& container,
		const MFrameContext& frameContext) const = 0;
	virtual void update(
		MSubSceneContainer& container,
		const MFrameContext& frameContext) = 0;
	virtual bool furtherUpdateRequired(
		const MFrameContext& frameContext);
	virtual bool areUIDrawablesDirty() const;
	virtual bool hasUIDrawables() const;
	virtual void addUIDrawables(
		MUIDrawManager& drawManager,
		const MFrameContext& frameContext);

	virtual bool getSelectionPath(
		const MRenderItem& renderItem, MDagPath& dagPath) const;

	virtual void updateSelectionGranularity(
		const MDagPath& path,
		MSelectionContext& selectionContext);

	MStatus setGeometryForRenderItem(
		MRenderItem& renderItem,
		const MVertexBufferArray& vertexBuffers,
		const MIndexBuffer& indexBuffer,
		const MBoundingBox* objectBox);

    unsigned int addInstanceTransform(
		MRenderItem& renderItem,
		const MMatrix& transform);
    MStatus setInstanceTransformArray(
		MRenderItem& renderItem,
		const MMatrixArray& matrixArray);
    MStatus updateInstanceTransform(
		MRenderItem& renderItem,
		unsigned int instanceId,
		const MMatrix& transform);
    MStatus removeInstance(
		MRenderItem& renderItem,
		unsigned int instanceId);
    MStatus removeAllInstances(MRenderItem& renderItem);

    MStatus setExtraInstanceData(
		MRenderItem& renderItem,
		const MString& parameterName,
		const MFloatArray& data);
	MStatus setExtraInstanceData(
		MRenderItem& renderItem,
		unsigned int instanceId,
		const MString& parameterName,
		const MFloatArray& data);
	MStatus removeExtraInstanceData(
		MRenderItem& renderItem,
		const MString& parameterName);

	MStatus setAllowTransparentInstances(MRenderItem& renderItem, bool allow);

	static const char* className();

private:

	void* fTempManager;
};

} // namespace MHWRender

#endif /* __cplusplus */
#endif /* _MPxSubSceneOverride */
