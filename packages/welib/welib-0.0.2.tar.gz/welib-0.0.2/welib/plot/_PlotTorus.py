import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from welib.plot.surface3d import *



X,Y,Z= torus(r=0.25, R=1, nTheta=32, nPhi=31, thetaMax=2*np.pi, phiMax=2*np.pi)
X,Y,Z = cylinder(R1=2, R2=1, z1=0, z2=1, nz=3, nTheta=15, thetaMax=2*np.pi)

theta=np.linspace(0,2*np.pi,30)
x=np.cos(theta)
y=np.sin(2*theta)
X,Y,Z = arbitrary_cylinder(x, y, z1=0, z2=1, nz=3, nTheta=25)


thetaMax=2*np.pi
nTheta=14

z1 = 0
z2 = 1
nz = 3
R1=2
R2=0


# arbitrary cylinder
# ADFile='../../data/NREL5MW/5MW_Baseline/NRELOffshrBsline5MW_AeroDyn.dat'
ADFile='../../data/NREL5MW/data/NREL5MW_AD15.05.dat'
#from welib.weio.fast_input_deck  import FASTInputDeck
from welib.tools.clean_exceptions import *
from weio.fast_input_deck  import FASTInputDeck

fst = FASTInputDeck()
fst.readAD(ADFile, readlist=['all'], verbose=True)

coords = fst.fst_vt['ac_data']
# bld = fst.fst_vt['AeroDynBlade']['BldAeroNodes']
bld = fst.fst_vt['AeroDynBlade'].toDataFrame()
# [:,6]
r       = bld['BlSpn_[m]'].values.astype(int)
ID      = bld['BlAFID_[-]'].values.astype(int)
chord   = bld['BlChord_[m]'].values
twist   = bld['BlTwist_[deg]'].values*np.pi/180
prebend = bld['BlCrvAC_[m]'].values
sweep   = bld['BlSwpAC_[m]'].values
print(bld)

print()
df = coords[4].toDataFrame()
x=df['x/c_[-]'].values
y=df['y/c_[-]'].values

fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')
# ax.set_aspect('equal')

for i in np.arange(len(r)-1): 
    z1=r[i]
    z2=r[i+1]
    print('z',z1,z2)
    id = ID[i]-1
    df = coords[id].toDataFrame()
    x=df['x/c_[-]'].values * chord[i]
    y=df['y/c_[-]'].values * chord[i]

    X,Y,Z = arbitrary_cylinder(x, y, z1=z1, z2=z2, nz=2, nTheta=25)

# Display the mesh
# ax.set_xlim3d(-1, 1)
# ax.set_ylim3d(-1, 1)
# ax.set_zlim3d(-1, 1)
    ax.plot_surface(X, Y, Z, color = 'w', rstride = 1, cstride = 1)

def axisEqual3D(ax):
    extents = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
    sz = extents[:,1] - extents[:,0]
    centers = np.mean(extents, axis=1)
    maxsize = max(abs(sz))
    r = maxsize/2
    for ctr, dim in zip(centers, 'xyz'):
        getattr(ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)
axisEqual3D(ax)

plt.show()
