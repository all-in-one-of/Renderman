#!/usr/bin/python
import prman
# import the python functions
import sys
sys.path.append('../common')
from Camera import *


ri = prman.Ri() # create an instance of the RenderMan interface

versionMajor=int(ri.PRMAN_VERSION_STR.split('.')[0])

filename = "__render" 
# this is the begining of the rib archive generation we can only
# make RI calls after this function else we get a core dump
ri.Begin('__render')

# on Version 20.12 openvdb plug is /etc  note on my mac the 
# subsitutions don't work so need full path (Bug?)
ri.Option("ribparse" , {"string varsubst" : ["$"]})
ri.Option( "searchpath", { "string procedural" : [".:${RMANTREE}/etc:${RMANTREE}/lib/plugins:/Applications/Pixar/RenderManProServer-22.3/lib/plugins"]})

ri.Option( "bucket" ,{"string order" : ["spiral"]})

# now we add the display element using the usual elements
# FILENAME DISPLAY Type Output format
ri.Display("vdb.exr", "openexr", "rgba")
ri.Format(1024,720,1)

# setup the raytrace / integrators

ri.Hider("raytrace" ,{"int incremental" :[1], "int minsamples" : [4] , "int maxsamples"  : [128]})
ri.PixelVariance (0.02)
ri.ShadingRate(0.5)
ri.Integrator ("PxrPathTracer" , "integrator" ,{ "int numLightSamples"  : [4] , "int numBxdfSamples" : [4],  "int maxPathLength" : [1]})

# now set the projection to perspective
ri.Projection(ri.PERSPECTIVE,{ri.FOV:30}) 
# Simple translate for our camera
cam=Camera(Vec4(2,2,10),Vec4(0,0,0),Vec4(0,1,0))
cam.place(ri)



# now we start our world
ri.WorldBegin()


ri.AttributeBegin()

ri.Declare("areaLight" ,"string")

ri.Light( "PxrDomeLight", 'domeLight',{ 
                                        "float exposure" : [1.0],
                                        "string lightColorMap" : ["../usingzip/studio2.tx"]
                                      })
ri.AttributeEnd()

# smoke

ri.AttributeBegin()
ri.Attribute( "visibility", { "int transmission" : [1]})

# we have a density value in the VDB file
ri.Pattern( "PxrPrimvar",  "primvar", {"string type" : ["float"], "string varname" : ["density"]})
# use a volume shader
ri.Bxdf( "PxrVolume", "smooth" , { "color diffuseColor" : [1, 1 ,1], 
                            "reference float densityFloat" : ["primvar:resultF"],
                            "float maxDensity" : [30] ,"int samples" : [8]})
# change this for speed.
ri.ShadingRate(0.2)


# now load the vdf as a volume
ri.Volume ("blobbydso:impl_openvdb.so", [-100, 100, -100 ,100, -100 ,100] ,[0, 0, 0] , {"constant string[2] blobbydso:stringargs" : ["teapot.vdb", "density"] ,  "varying float density" : [] })


ri.AttributeEnd()



# floor
ri.TransformBegin()
ri.Translate(0,-0.5,0)
ri.Bxdf( "PxrDisney","bxdf", { 
                        "color baseColor" : [ 1.0,1.0,1.0]
                        })
s=5.0
face=[-s,0,-s, s,0,-s,-s,0,s, s,0,s]
ri.Patch("bilinear",{'P':face})

ri.TransformEnd()



# end our world
ri.WorldEnd()
# and finally end the rib file
ri.End()
