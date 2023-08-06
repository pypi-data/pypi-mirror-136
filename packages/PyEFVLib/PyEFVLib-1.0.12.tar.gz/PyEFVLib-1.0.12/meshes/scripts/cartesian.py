import numpy as np
import meshio

width  = 1
height = 1
nx = 30
ny = 30

x = np.linspace(0,width,nx+1)
y = np.linspace(0,height,ny+1)

xv,yv = np.meshgrid(x,y)
xv.resize(xv.size); yv.resize(yv.size)

points = np.array(list(zip(xv,yv)))
points = np.concatenate((points.T,[np.zeros(len(points))])).T

idx = lambda i,j: i+(nx+1)*j
quad_cells = np.array([[idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)] for j in range(ny) for i in range(nx)])
line_cells = np.array([ [idx(*(p,q)[ ::(1,-1)[k] ]), idx(*(p+1,q)[ ::(1,-1)[k] ])] for k in range(2) for q in (0,(ny,nx)[k]) for p in range((nx,ny)[k]) ])

quad_data = np.ones(len(quad_cells), dtype=np.int32)
line_data = np.array(nx*[2]+nx*[3]+ny*[4]+ny*[5], dtype=np.int32)

cells = [("line",line_cells), ("quad",quad_cells),]
cell_data = {"gmsh:physical":[line_data, quad_data],"gmsh:geometrical":[line_data, quad_data]}

field_data = {"Body":[1,2], "South":[2,1], "North":[3,1], "West":[4,1], "East":[5,1]}

mesh = meshio.Mesh(points, cells, cell_data=cell_data, field_data=field_data)

mesh.write("output.msh", file_format="gmsh22", binary=False)