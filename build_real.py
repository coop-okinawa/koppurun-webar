import os, math, numpy as np, trimesh
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from trimesh.visual.material import PBRMaterial
rng=np.random.default_rng(20261009)
scene=trimesh.Scene()
RED=[213,24,54,255]; DARK=[12,13,18,255]; WHITE=[255,255,255,255]; GREEN=[29,139,65,255]
def add(m,color,name,noise=0):
    n=len(m.vertices); c=np.tile(np.array(color,dtype=float),(n,1))
    if noise:
        vals=rng.normal(0,noise,n)
        c[:,:3]=np.clip(c[:,:3]+vals[:,None],0,255)
    m.visual.vertex_colors=c.astype('uint8');scene.add_geometry(m,geom_name=name)
def ball(name,center,radii,color,sub=3):
    m=trimesh.creation.icosphere(subdivisions=sub,radius=1)
    m.vertices=m.vertices*np.array(radii)+np.array(center)
    add(m,color,name,2.8 if color==RED else 1.5)
def tube(name,pts,radius,color,sections=10):
    pts=np.asarray(pts)
    for i,(a,b) in enumerate(zip(pts[:-1],pts[1:])):
        vec=b-a;length=np.linalg.norm(vec)
        if length<1e-5:continue
        m=trimesh.creation.cylinder(radius=radius,height=length,sections=sections)
        m.apply_transform(trimesh.geometry.align_vectors([0,0,1],vec));m.apply_translation((a+b)/2)
        add(m,color,f'{name}_{i}')
    for j,p in enumerate(pts[1:-1]):ball(f'{name}_join_{j}',p,[radius]*3,color,1)
# Fabric texture: low contrast woven plush with uneven dye, not source photograph
S=1024
noise=rng.normal(0,1,(S,S))
from PIL import ImageFilter
cloud=Image.fromarray(np.uint8(np.clip(noise*25+127,0,255))).filter(ImageFilter.GaussianBlur(18))
cloud=np.array(cloud).astype(float)-127
fine=rng.normal(0,1,(S,S))*3.2
weave=(np.sin(np.arange(S)[:,None]*1.3)*np.sin(np.arange(S)[None,:]*1.1))*2
v=cloud*.75+fine+weave
rgb=np.zeros((S,S,4),dtype='uint8')
for i,x in enumerate(RED[:3]):rgb[:,:,i]=np.clip(x+v,0,255)
rgb[:,:,3]=255
fabric=Image.fromarray(rgb,'RGBA')
# body UV sphere, modified near base to resemble a slightly flattened plush costume
m=trimesh.creation.uv_sphere(radius=1,count=[96,96])
pos=m.vertices.copy()
x,y,z=pos[:,0],pos[:,1],pos[:,2]
# sphere y is vertical; transform into 1.7m wide apple-shaped body
m.vertices=np.column_stack([x*.86*(1+.035*y),1.19+y*.77,z*.71])
uv=np.column_stack([.5+np.arctan2(z,x)/(2*np.pi),.5+np.arcsin(np.clip(y,-1,1))/np.pi])
m.visual=trimesh.visual.TextureVisuals(uv=uv,material=PBRMaterial(baseColorTexture=fabric,metallicFactor=0,roughnessFactor=.96,doubleSided=True))
scene.add_geometry(m,geom_name='textured_plush_body')
# slightly raised crown and low profile feet
ball('crown',(0,1.78,-.04),(.46,.16,.43),RED,4)
for s in [-1,1]:
    ball(f'leg_{s}',(s*.35,.30,.04),(.23,.28,.25),RED,3)
    ball(f'foot_{s}',(s*.36,.17,.19),(.24,.17,.33),RED,4)
    ball(f'arm_{s}',(s*.84,.78,.03),(.18,.24,.20),RED,3)
    ball(f'hand_{s}',(s*.98,.68,.13),(.17,.17,.20),RED,3)
# eyes front with curved reflection
for s in [-1,1]:
    x=s*.47
    ball(f'eye_{s}',(x,1.17,.600),(.117,.157,.064),DARK,4)
    ball(f'eye_white_{s}',(x-s*.037,1.19,.665),(.034,.088,.013),WHITE,3)
    ball(f'eye_cutout_{s}',(x-s*.004,1.19,.678),(.027,.079,.008),DARK,3)
pts=[]
for t in np.linspace(np.pi,2*np.pi,28):
    x=.142*np.cos(t);pts.append((x,1.043+.09*np.sin(t),.724))
tube('mouth',pts,.031,DARK,12)
ball('stem',(0,1.98,-.055),(.071,.19,.073),GREEN,3)
# ring leaf with actual hole
outer=[];inner=[]
for t in np.linspace(0,2*np.pi,65)[:-1]:
    outer.append([.13+.24*np.cos(t)+.05*np.sin(t),2.035+.17*np.sin(t),-.015])
    inner.append([.13+.095*np.cos(t),2.035+.072*np.sin(t),-.015])
n=len(outer);verts=[]
for zoff in [-.037,.037]:
    for a in (outer,inner):verts.extend([[p[0],p[1],p[2]+zoff] for p in a])
faces=[]
for i in range(n):
 j=(i+1)%n
 for a,b,c,d in [(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j),(i,n+i,n+j,j),(2*n+i,2*n+j,3*n+j,3*n+i)]:faces.extend([[a,b,c],[a,c,d]])
leaf=trimesh.Trimesh(vertices=verts,faces=faces,process=False);add(leaf,GREEN,'leaf_with_hole',2)
# white lettering (prototype: flat patch, not perfectly projected onto plush surface)
W,H=512,256
im=Image.new('RGBA',(W,H),(255,255,255,0));d=ImageDraw.Draw(im)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=ImageFont.truetype(fontpath,123)
d.text((12,28),'COOP',font=font,fill=(255,255,255,255))
a=math.radians(55);u=np.array([math.cos(a),math.sin(a),0]);v=np.array([-math.sin(a),math.cos(a),0]);center=np.array([-.49,1.59,.590]);w,h=.47,.19
vertices=np.array([center+u*i*w/2+v*j*h/2 for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]])
logo=trimesh.Trimesh(vertices=vertices,faces=[[0,1,2],[0,2,3]],process=False)
logo.visual=trimesh.visual.TextureVisuals(uv=[[0,0],[1,0],[1,1],[0,1]],material=PBRMaterial(baseColorTexture=im,alphaMode='BLEND',doubleSided=True,metallicFactor=0,roughnessFactor=1))
scene.add_geometry(logo,geom_name='white_coop_lettering')
# subtle back seam
seam=[]
for t in np.linspace(-1.05,1.05,24):
    seam.append((.09,1.19+t*.65,-.708*np.sqrt(max(.04,1-t*t))))
tube('rear_stitch',seam,.004,[175,20,44,255],8)
scene.export(os.path.join(os.path.dirname(__file__),'koppurun_real.glb'))
print('GLB created:',len(scene.geometry),'meshes')
