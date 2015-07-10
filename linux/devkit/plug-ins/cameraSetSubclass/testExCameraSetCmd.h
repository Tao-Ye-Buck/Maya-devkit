//-
// ==========================================================================
// Copyright (C) 1995 - 2006 Autodesk, Inc. and/or its licensors.  All 
// rights reserved.
//
// The coded instructions, statements, computer programs, and/or related 
// material (collectively the "Data") in these files contain unpublished 
// information proprietary to Autodesk, Inc. ("Autodesk") and/or its 
// licensors, which is protected by U.S. and Canadian federal copyright 
// law and by international treaties.
//
// The Data is provided for use exclusively by You. You have the right 
// to use, modify, and incorporate this Data into other products for 
// purposes authorized by the Autodesk software license agreement, 
// without fee.
//
// The copyright notices in the Software and this entire statement, 
// including the above license grant, this restriction and the 
// following disclaimer, must be included in all copies of the 
// Software, in whole or in part, and all derivative works of 
// the Software, unless such copies or derivative works are solely 
// in the form of machine-executable object code generated by a 
// source language processor.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. 
// AUTODESK DOES NOT MAKE AND HEREBY DISCLAIMS ANY EXPRESS OR IMPLIED 
// WARRANTIES INCLUDING, BUT NOT LIMITED TO, THE WARRANTIES OF 
// NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A PARTICULAR 
// PURPOSE, OR ARISING FROM A COURSE OF DEALING, USAGE, OR 
// TRADE PRACTICE. IN NO EVENT WILL AUTODESK AND/OR ITS LICENSORS 
// BE LIABLE FOR ANY LOST REVENUES, DATA, OR PROFITS, OR SPECIAL, 
// DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES, EVEN IF AUTODESK 
// AND/OR ITS LICENSORS HAS BEEN ADVISED OF THE POSSIBILITY 
// OR PROBABILITY OF SUCH DAMAGES.
//
// ==========================================================================
//+

//
// testCameraSetCmd.h
//
// Description:
//     Sample plug-in that exercises the exCameraSet class
//
//	   testExCameraSet -help will list the options.
//
// Example usages:
// testExCameraSet -c;
// testExCameraSet -ac persp cameraSet1;
// testExCameraSet -ac top cameraSet1;
// testExCameraSet -d 0 cameraSet1;
// testExCameraSet -q -camera -layer 0 cameraSet1;
// testExCameraSet -e -camera side -layer 0 cameraSet1;
// testExCameraSet -e -set defaultObjectSet -layer 0 cameraSet1;
// testExCameraSet -q -set -layer 0 cameraSet1;
// testExCameraSet -e -set "" -layer 0 cameraSet1;
// testExCameraSet -e -layerType Left -layer 0 cameraSet1;
// testExCameraSet -q -layerType -layer 0 cameraSet1;
// testExCameraSet -e -active true -layer 0 cameraSet1;
// testExCameraSet -q -active -layer 0 cameraSet1;
// testExCameraSet -q -numLayers cameraSet1;
//
//
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>

class MArgList;

#define kCmdName "testExCameraSet"

//////////////////////////////////////////////////////////////////////////
//
// Command class declaration
//
//////////////////////////////////////////////////////////////////////////

class testExCameraSetCmd : public MPxCommand
{
public:
					testExCameraSetCmd() {};
	virtual			~testExCameraSetCmd(); 
	MStatus			doIt( const MArgList& args );

	static void*	creator();
private:
	MStatus			parseArgs(const MArgList &args);
	bool 			getExCameraSetNode(MObject &dirObj);

	bool 			createUsed;
	bool 			editUsed;
	bool 			queryUsed;
	bool 			activeUsed;
	bool 			appendCameraUsed;
	bool 			appendCameraAndSetUsed;
	bool 			cameraUsed;
	bool 			deleteLayerUsed;
	bool 			numLayersUsed;
	bool 			layerUsed;
	bool 			layerTypeUsed;
	bool 			setUsed;
	bool 			helpUsed;

	unsigned int	cameraLayer;
	bool			activeVal;
	MString			camName;
	MString			setName;
	MString			layerTypeVal;
	MSelectionList	list;

};


