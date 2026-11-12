import trimesh, numpy as np
S=2.5
src=trimesh.load("dl/clawd.stl"); sc=trimesh.load("dl/clawd_singlecolor.stl")
def scaled(m):
    m=m.copy(); m.apply_scale(S); return m
a=scaled(src); b=scaled(sc)
a.export("out/clawd_2.5x.stl"); b.export("out/clawd_2.5x_singlecolor.stl")
# split raised-eye model into body + eyes for previews / dual-colour
z=a.triangles_center[:,2]
body=a.copy(); 
# body = extrude of everything below z=33*S; rebuild by clipping
body=trimesh.intersections.slice_mesh_plane(a,[0,0,-1],[0,0,33*S],cap=True)
eyes=trimesh.intersections.slice_mesh_plane(a,[0,0,1],[0,0,33*S],cap=True)
body.fix_normals(); eyes.fix_normals(); print("vol",body.volume>0,eyes.volume>0)
body.export("out/_body.stl"); eyes.export("out/_eyes.stl")
for n,m in [("full",a),("singlecolor",b),("body",body),("eyes",eyes)]:
    print(n,m.extents.round(2).tolist(),"wt",m.is_watertight,"vol cm3",round(m.volume/1000,1),"parts",len(m.split()))
