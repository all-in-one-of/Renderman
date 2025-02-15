#!/usr/bin/python
import prman
# import the python functions
import sys
import sys,os.path,subprocess
import argparse

# Main rendering routine
def main(filename,shadingrate=10,pixelvar=0.1,
         fov=48.0,width=1024,height=720,
         integrator='PxrPathTracer',integratorParams={}
        ) :
  print 'shading rate {} pivel variance {} using {} {}'.format(shadingrate,pixelvar,integrator,integratorParams)
  ri = prman.Ri() # create an instance of the RenderMan interface

  # this is the begining of the rib archive generation we can only
  # make RI calls after this function else we get a core dump
  ri.Begin(filename)
  ri.Option('searchpath', {'string archive':'./assets/:@'})
  ri.Option('searchpath', {'string texture':'./textures/:@'})

  # now we add the display element using the usual elements
  # FILENAME DISPLAY Type Output format
  ri.Display('rgb.exr', 'it', 'rgba')
  ri.Format(width,height,1)

  # setup the raytrace / integrators
  ri.Hider('raytrace' ,{'int incremental' :[1]})
  ri.ShadingRate(shadingrate)
  ri.PixelVariance (pixelvar)
  ri.Integrator (integrator ,'integrator',integratorParams)
  ri.Option( 'statistics', {'filename'  : [ 'stats.txt' ] } )
  ri.Option( 'statistics', {'endofframe' : [ 1 ] })
 
  ri.Projection(ri.PERSPECTIVE,{ri.FOV:fov})

  ri.Rotate(12,1,0,0)
  ri.Translate( 0, 0.75 ,2.5)


  # now we start our world
  ri.WorldBegin()
  #######################################################################
  #Lighting We need geo to emit light
  #######################################################################
  ri.TransformBegin()
  ri.AttributeBegin()
  ri.Declare('sphereLight' ,'string')
  ri.Translate(1.8,0.6,0)
  #ri.Rotate(90,1,0,0)
  ri.Scale(0.4, 0.5, 0.4)

  ri.Light( 'PxrSphereLight', 'sphereLight', { 
            'float exposure' : 3.2,
            'float intensity' : 13.0
   })
  ri.AttributeEnd()
  ri.TransformEnd()
  #######################################################################
  # end lighting
  #######################################################################

  ri.AttributeBegin()
  ri.Attribute( 'identifier',{ 'name' :'cornell'})
  ri.Bxdf('PxrDiffuse', 'left' ,{
          'color diffuseColor' :[0.8 ,0.2 ,0.2]
          })
  ri.Polygon( {ri.P : [-1 ,1, -5,  -1, 1, 1,  -1, -1, 1,  -1, -1, -5]})
  ri.Bxdf('PxrDiffuse', 'floor',{ 
          'color diffuseColor' : [0.8, 0.8, 0.8]
          })
  ri.Polygon( {ri.P : [-1 ,-1, 1,  1, -1, 1 , 1, -1, -5,  -1, -1, -5]})
  ri.Bxdf('PxrDiffuse' ,'ceiling',{ 
          'color diffuseColor' :[0.95, 0.95, 0.95]
          })
  ri.Polygon( {ri.P : [-1 ,1 ,-5,  1, 1, -5,  1, 1, 1,  -1, 1 ,1]})
  ri.Bxdf('PxrDiffuse', 'back' ,{
          'color diffuseColor' : [0.8, 0.8, 0.8]
          })
  ri.Polygon( {ri.P : [-1 ,1 ,1 , 1 ,1 ,1,  1, -1, 1,  -1, -1, 1]})
  ri.AttributeEnd()

  ri.AttributeBegin()
  ri.Attribute( 'identifier',{ 'name' :'buddha'})
  ri.TransformBegin()
  ri.Translate(-0.5,-1,0)
  ri.Rotate(180,0,1,0)
  ri.Scale(0.1,0.1,0.1)
  ri.Attribute( 'visibility',{ 'int transmission' : [1]})
  ri.Attribute( 'trace',
  { 
    'int maxdiffusedepth' : [1], 
    'int maxspeculardepth' : [8]
  })
  ri.Bxdf('PxrSurface', 'greenglass',{ 
  'color refractionColor' : [0,0.9,0],
  'float diffuseGain' : 0,
  'color specularEdgeColor' : [0.2, 1 ,0.2],
  'float refractionGain' : [1.0],
  'float reflectionGain' : [1.0],
  'float glassRoughness' : [0.01],
  'float glassIor' : [1.5],
  'color extinction' : [0.0, 0.2 ,0.0],
  
  })

  ri.ReadArchive('buddha.zip!buddha.rib')
  ri.TransformEnd()
  ri.AttributeEnd()

  ri.AttributeBegin()
  ri.Attribute( 'identifier',{ 'name' :'sphere'})
  ri.Pattern('PxrVariable','du', {'string variable': 'du', 'string type' : 'float'})
  ri.Pattern('PxrVariable','dv', {'string variable': 'dv', 'string type' : 'float'})
  ri.Pattern('starBall','starBall', { 
            'reference float du' : ['du:resultR'], 
            'reference float dv' : ['dv:resultR']
            })

  ri.Bxdf('PxrDisney','bxdf', { 
          'reference color baseColor' : ['starBall:Cout'] 
          })
  ri.TransformBegin()
  ri.Translate(0.3, -0.7 , 0.3)
  ri.Rotate(-30,0,1,0)
  ri.Rotate(20,1,0,0)
  ri.Sphere(0.3,-0.3,0.3,360)
  ri.TransformEnd()
  ri.AttributeEnd()

  ri.AttributeBegin()
  ri.Attribute( 'identifier',{ 'name' :'teapot'})
  ri.TransformBegin()
  ri.Translate(0, -1 , -0.8)
  ri.Rotate(45,0,1,0)
  ri.Rotate( -90, 1 ,0 ,0)
  ri.Scale( 0.1, 0.1, 0.1) 
  ri.Bxdf('PxrSurface', 'plastic',{
          'color diffuseColor' : [.04, .51, .1],
          'color clearcoatFaceColor' : [.5, .5, .5], 
          'color clearcoatEdgeColor' : [.25, .25, .25]
  })
  ri.Geometry('teapot')
  ri.TransformEnd()
  ri.AttributeEnd()

  ri.AttributeBegin()
  ri.Bxdf('PxrSurface', 'metal', 
  {
          'float diffuseGain' : [0],
          'int specularFresnelMode' : [1],
          'color specularEdgeColor' : [1 ,1 ,1],
          'color specularIor' : [4.3696842, 2.916713, 1.654698],
          'color specularExtinctionCoeff' : [5.20643, 4.2313662, 3.7549689],
          'float specularRoughness' : [0.1], 
          'integer specularModelType' : [1] 
  })

  ri.Attribute('identifier',{ 'name' :'ncca'})
  ri.TransformBegin()
  ri.Translate(0, 0.3 , 0.8)
  ri.ReadArchive('ncca.rib')
  ri.TransformEnd()
  ri.AttributeEnd()

# Volume in box
  ri.AttributeBegin() 
  ri.Bxdf('PxrVolume', 'smooth',{ 
          'float densityFloat' : 0.95,
          'float anisotropy' : 0.2
          })
  ri.Volume('box',[-0.999,0.999,-0.999,0.999,-0.999,0.999], [0, 0, 0])
  ri.AttributeEnd() 


  ri.AttributeBegin() 
  #Attribute 'dice' 'rasterorient' 0
  ri.Attribute('identifier' , {'name' : 'stainedglass_rightwall'})
  ri.Pattern('PxrManifold2D' ,'texture_place',{ 
             'float scaleS' : [1], 
             'float scaleT' : [1]})
  ri.Pattern('PxrTexture', 'ctex1', {
             'string filename' : ['stainedGlass.tex'], 
             'int invertT' : [0] , 
             'reference struct manifold' : ['texture_place:result']
             })
  # build an expression to set the colour based on UV position so the whole area is not the light. So basically texture is output in uv range .25 - .75 blue if not (for cornell box)
  diffuseExpr='''
  $u > .25 &&  $u < .75 && $v > .25 &&  $v < .75 ? $inColor: [0.2 ,0.2, 0.8]
  '''
  ri.Pattern( 'PxrSeExpr', 'diffuse' , {'reference color inColor' : 'ctex1:resultRGB' , 'string expression' : diffuseExpr})
  # this expression is for the transmission colour, only transmit if in texture range.
  transmitExpr='''
  $u > .25 &&  $u < .75 && $v > .25 &&  $v < .75 ? $inColor: 0
  '''
  ri.Pattern( 'PxrSeExpr' ,'transmit', {'reference color inColor' : 'ctex1:resultRGB', 'string expression' : transmitExpr})
  ri.Bxdf( 'PxrSurface', 'stained', {
           'float diffuseGain' : [1],
           'integer diffuseDoubleSided'  :[1], 
  'reference color diffuseColor' : ['diffuse:resultRGB'], 
  'reference color diffuseTransmitColor' : ['transmit:resultRGB'],
  'reference color shadowColor' :['transmit:resultRGB'] ,
  'int presenceCached' :[1] }) # opacity cached by default
  ri.Patch( 'bilinear', {ri.P : [1, -1, -1 ,1, -1, 1, 1, 1, -1, 1, 1, 1], 'varying float s' : [1, 0, 1 ,0], 'varying float t' : [1, 1, 0, 0]})
  ri.AttributeEnd() 





  # end our world
  ri.WorldEnd()
  # and finally end the rib file
  ri.End()



def checkAndCompileShader(shader) :
  	if os.path.isfile(shader+'.oso') != True  or os.stat(shader+'.osl').st_mtime - os.stat(shader+'.oso').st_mtime > 0 :
		print 'compiling shader %s' %(shader)
		try :
			subprocess.check_call(['oslc', shader+'.osl'])
		except subprocess.CalledProcessError :
			sys.exit('shader compilation failed')
		 


if __name__ == '__main__':
  shaderName='starBall'
  checkAndCompileShader(shaderName)
  
  parser = argparse.ArgumentParser(description='Modify render parameters')
  
  parser.add_argument('--shadingrate', '-s', nargs='?', 
                      const=10.0, default=10.0, type=float,
                      help='modify the shading rate default to 10')

  parser.add_argument('--pixelvar', '-p' ,nargs='?', 
                      const=0.1, default=0.1,type=float,
                      help='modify the pixel variance default  0.1')
  parser.add_argument('--fov', '-f' ,nargs='?', 
                      const=48.0, default=48.0,type=float,
                      help='projection fov default 48.0')
  parser.add_argument('--width' , '-wd' ,nargs='?', 
                      const=1024, default=1024,type=int,
                      help='width of image default 1024')
  parser.add_argument('--height', '-ht' ,nargs='?', 
                      const=720, default=720,type=int,
                      help='height of image default 720')
  
  parser.add_argument('--rib', '-r' , action='count',help='render to rib not framebuffer')
  parser.add_argument('--default', '-d' , action='count',help='use PxrDefault')
  parser.add_argument('--vcm', '-v' , action='count',help='use PxrVCM')
  parser.add_argument('--direct', '-t' , action='count',help='use PxrDirect')
  parser.add_argument('--wire', '-w' , action='count',help='use PxrVisualizer with wireframe shaded')
  parser.add_argument('--normals', '-n' , action='count',help='use PxrVisualizer with wireframe and Normals')
  parser.add_argument('--st', '-u' , action='count',help='use PxrVisualizer with wireframe and ST')

  args = parser.parse_args()
  if args.rib :
    filename = 'rgb.rib' 
  else :
    filename='__render'
  
  integratorParams={}
  integrator='PxrPathTracer'
  if args.default :
    integrator='PxrDefault'
  if args.vcm :
    integrator='PxrVCM'
  if args.direct :
    integrator='PxrDirectLighting'
  if args.wire :
    integrator='PxrVisualizer'
    integratorParams={'int wireframe' : [1], 'string style' : ['shaded']}
  if args.normals :
    integrator='PxrVisualizer'
    integratorParams={'int wireframe' : [1], 'string style' : ['normals']}
  if args.st :
    integrator='PxrVisualizer'
    integratorParams={'int wireframe' : [1], 'string style' : ['st']}


  main(filename,args.shadingrate,args.pixelvar,args.fov,args.width,args.height,integrator,integratorParams)

