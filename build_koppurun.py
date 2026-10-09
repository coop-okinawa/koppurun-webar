import os

import numpy as np, trimesh, math
from trimesh.transformations import rotation_matrix
from PIL import Image,ImageDraw,ImageFont
from trimesh.visual.material import PBRMaterial
scene=trimesh.Scene()
RED=[211,21,55,255]; DARK=[15,17,23,255]; WHITE=[255,255,255,255]; GREEN=[27,143,65,255]
def add(m,color,name):
    m.visual.vertex_colors=np.tile(np.array(color,dtype=np.uint8),(len(m.vertices),1))
    scene.add_geometry(m,geom_name=name)
def ball(name,center,radii,color,sub=3):
    m=trimesh.creation.icosphere(subdivisions=sub,radius=1)
    m.vertices=m.vertices*np.array(radii)+np.array(center)
    add(m,color,name)
def tube(name,pts,radius,color,sections=10):
    pts=np.asarray(pts)
    for i,(a,b) in enumerate(zip(pts[:-1],pts[1:])):
        vec=b-a; length=np.linalg.norm(vec)
        if length<1e-5:continue
        m=trimesh.creation.cylinder(radius=radius,height=length,sections=sections)
        m.apply_transform(trimesh.geometry.align_vectors([0,0,1],vec))
        m.apply_translation((a+b)/2)
        add(m,color,f'{name}_{i}')
    for j,p in enumerate(pts[1:-1]):ball(f'{name}_join_{j}',p,[radius]*3,color,1)
# body: rounded plush apple body, bottom subtly narrower
ball('red_apple_body',(0,1.18,0),(.84,.77,.73),RED,5)
# apple crown gentle bump
ball('top_crown',(0,1.77,-.02),(.48,.19,.44),RED,3)
# legs and oversized plush shoes
for s in [-1,1]:
    ball(f'leg_{s}',(s*.38,.28,.06),(.23,.30,.26),RED,3)
    ball(f'foot_{s}',(s*.38,.16,.21),(.25,.16,.34),RED,3)
    ball(f'arm_{s}',(s*.84,.81,.03),(.18,.25,.21),RED,3)
    ball(f'hand_{s}',(s*1.01,.69,.17),(.17,.18,.20),RED,3)
# eyes: black vertical ovals on curved face, white crescent reflection
for s in [-1,1]:
    x=s*.47
    ball(f'eye_black_{s}',(x,1.14,.603),(.115,.156,.067),DARK,4)
    ball(f'eye_glint_{s}',(x-s*.033,1.16,.668),(.032,.087,.016),WHITE,3)
    ball(f'eye_inner_{s}',(x-s*.005,1.16,.680),(.025,.081,.009),DARK,3)
# small smiling mouth with upward tips (front-facing U)
points=[]
for theta in np.linspace(math.pi,2*math.pi,20):
    # arc: ends high, bottom low
    x=.145*math.cos(theta); y=1.045+.090*math.sin(theta)
    z=.735 - .02*(x/.145)**2
    points.append((x,y,z))
tube('smile',points,.032,DARK,12)
# green stem
ball('green_stem',(0,1.955,-.055),(.075,.22,.085),GREEN,3)
# leaf as flattened ring in XY plane (actual open hole), slightly tilted
# ring shape has pointed leaf-tip silhouette and actual empty center
outer=[];inner=[]
for t in np.linspace(0,2*math.pi,49)[:-1]:
    outer.append([.12+.24*math.cos(t)+.06*math.sin(t),2.045+.165*math.sin(t)+.02*math.cos(t),-.02])
    inner.append([.12+.095*math.cos(t),2.045+.075*math.sin(t),-.02])
verts=[]
for zoff in [-.04,.04]:
    for p in outer:verts.append([p[0],p[1],p[2]+zoff])
    for p in inner:verts.append([p[0],p[1],p[2]+zoff])
n=len(outer);faces=[]
for i in range(n):
    j=(i+1)%n
    for a,b,c,d in [(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j),
                    (i,n+i,n+j,j),(2*n+i,2*n+j,3*n+j,3*n+i)]:
        faces.extend([[a,b,c],[a,c,d]])
m=trimesh.Trimesh(vertices=np.array(verts),faces=np.array(faces),process=False)
add(m,GREEN,'open_center_green_leaf')
# white COOP lettering on front upper left, alpha-textured curved patch
W,H=512,256
im=Image.new('RGBA',(W,H),(255,255,255,0));d=ImageDraw.Draw(im)
fonts=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']
font=next((ImageFont.truetype(p,130) for p in fonts if os.path.exists(p)),ImageFont.load_default())
d.text((16,30),'COOP',font=font,fill=(255,255,255,255))
# patch at upper left front, rotated around z axis to tilt
angle=np.radians(56)
u=np.array([np.cos(angle),np.sin(angle),0])
v=np.array([-np.sin(angle),np.cos(angle),0])
center=np.array([-.49,1.57,.595])
w,h=.48,.20
vertices=np.array([center+u*a*w/2+v*b*h/2 for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]])
uv=np.array([[0,0],[1,0],[1,1],[0,1]])
mesh=trimesh.Trimesh(vertices=vertices,faces=[[0,1,2],[0,2,3]],process=False)
mat=PBRMaterial(baseColorTexture=im,alphaMode='BLEND',doubleSided=True,metallicFactor=0,roughnessFactor=1)
mesh.visual=trimesh.visual.TextureVisuals(uv=uv,material=mat)
scene.add_geometry(mesh,geom_name='COOP_white_lettering')
scene.export('koppurun.glb')
print('Exported koppurun.glb; geometry parts:',len(scene.geometry))
