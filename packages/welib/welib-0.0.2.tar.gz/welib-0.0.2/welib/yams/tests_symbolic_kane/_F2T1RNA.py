"""
Equations of motion
model name: F2T1RNA
"""
import numpy as np
from numpy import cos, sin, pi, sqrt
def info():
    """ Return information about current model present in this package """
    I=dict()
    I['name']='F2T1RNA'
    I['nq']=3
    I['nu']=1
    I['sq']=['x','phi_y','q_T1']
    I['su']=['T_a']
    return I

def forcing(t,q=None,qd=None,p=None,u=None,z=None):
    """ Non linear mass forcing 
    q:  degrees of freedom, array-like: ['x(t)', 'phi_y(t)', 'q_T1(t)']
    qd: dof velocities, array-like
    p:  parameters, dictionary with keys: ['DD_T', 'KK_T', 'L_T', 'MM_T', 'M_F', 'M_RNA', 'g', 'tilt', 'v_yT1c', 'x_NR', 'x_RNAG', 'z_FG', 'z_NR', 'z_RNAG']
    u:  inputs, dictionary with keys: ['T_a']
           where each values is a function of time
    """
    if z is not None:
        q  = z[0:int(len(z)/2)] 
        qd = z[int(len(z)/2): ] 
    FF = np.zeros((3,1))
    FF[0,0] = 2*p['MM_T'][0,6]*q[1]*qd[1]*qd[2]-p['MM_T'][1,3]*q[1]*qd[1]**2+p['L_T']*p['M_RNA']*q[1]*qd[1]**2+p['M_F']*p['z_FG']*q[1]*qd[1]**2-2*p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[1]*q[2]*qd[1]*qd[2]+p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*qd[2]**2+p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[1]*qd[2]**2+2*p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[2]*qd[1]*qd[2]-p['M_RNA']*p['v_yT1c']*p['x_RNAG']*q[1]*q[2]*qd[1]**2+2*p['M_RNA']*p['v_yT1c']*p['x_RNAG']*qd[1]*qd[2]+2*p['M_RNA']*p['v_yT1c']*p['z_RNAG']*q[1]*qd[1]*qd[2]+p['M_RNA']*p['v_yT1c']*p['z_RNAG']*q[2]*qd[1]**2+p['M_RNA']*p['x_RNAG']*qd[1]**2+p['M_RNA']*p['z_RNAG']*q[1]*qd[1]**2+2*p['M_RNA']*q[1]*qd[1]*qd[2]+p['M_RNA']*q[2]*qd[1]**2-p['v_yT1c']*q[1]*q[2]*u['T_a'](t,q,qd)-p['v_yT1c']*q[2]*p['tilt']*u['T_a'](t,q,qd)+u['T_a'](t,q,qd)
    FF[1,0] = -p['MM_T'][1,3]*p['g']*q[1]+p['L_T']*p['M_RNA']*p['g']*q[1]+p['L_T']*p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*qd[2]**2+2*p['L_T']*p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[2]*qd[1]*qd[2]+2*p['L_T']*p['M_RNA']*p['v_yT1c']*p['x_RNAG']*qd[1]*qd[2]-p['L_T']*p['v_yT1c']*q[2]*p['tilt']*u['T_a'](t,q,qd)+p['L_T']*u['T_a'](t,q,qd)+p['M_F']*p['g']*p['z_FG']*q[1]-p['M_RNA']*p['g']*p['v_yT1c']*p['x_RNAG']*q[1]*q[2]+p['M_RNA']*p['g']*p['v_yT1c']*p['z_RNAG']*q[2]+p['M_RNA']*p['g']*p['x_RNAG']+p['M_RNA']*p['g']*p['z_RNAG']*q[1]+p['M_RNA']*p['g']*q[2]+2*p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[2]**2*qd[1]*qd[2]-p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[2]*qd[2]**2-4*p['M_RNA']*p['v_yT1c']*p['z_RNAG']*q[2]*qd[1]*qd[2]-2*p['M_RNA']*p['x_RNAG']*qd[1]*qd[2]-2*p['M_RNA']*q[2]*qd[1]*qd[2]+p['v_yT1c']*q[2]**2*u['T_a'](t,q,qd)+p['x_NR']*p['tilt']*u['T_a'](t,q,qd)+p['z_NR']*u['T_a'](t,q,qd)+q[2]*p['tilt']*u['T_a'](t,q,qd)
    FF[2,0] = p['MM_T'][0,6]*p['g']*q[1]-p['DD_T'][6,6]*qd[2]-p['KK_T'][6,6]*q[2]-p['L_T']*p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[2]*qd[1]**2-p['L_T']*p['M_RNA']*p['v_yT1c']*p['x_RNAG']*qd[1]**2-p['M_RNA']*p['g']*p['v_yT1c']**2*p['x_RNAG']*q[1]*q[2]+p['M_RNA']*p['g']*p['v_yT1c']**2*p['z_RNAG']*q[2]+p['M_RNA']*p['g']*p['v_yT1c']*p['x_RNAG']+p['M_RNA']*p['g']*p['v_yT1c']*p['z_RNAG']*q[1]+p['M_RNA']*p['g']*q[1]-p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[2]**2*qd[1]**2+p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*qd[2]**2+2*p['M_RNA']*p['v_yT1c']*p['z_RNAG']*q[2]*qd[1]**2+p['M_RNA']*p['x_RNAG']*qd[1]**2+p['M_RNA']*q[2]*qd[1]**2+p['v_yT1c']*p['x_NR']*p['tilt']*u['T_a'](t,q,qd)+p['v_yT1c']*p['z_NR']*u['T_a'](t,q,qd)-p['v_yT1c']*q[2]*p['tilt']*u['T_a'](t,q,qd)+u['T_a'](t,q,qd)
    return FF

def mass_matrix(q=None,p=None,z=None):
    """ Non linear mass matrix 
     q:  degrees of freedom, array-like: ['x(t)', 'phi_y(t)', 'q_T1(t)']
     p:  parameters, dictionary with keys: ['J_yy_F', 'J_yy_RNA', 'L_T', 'MM_T', 'M_F', 'M_RNA', 'v_yT1c', 'x_RNAG', 'z_FG', 'z_RNAG']
    """
    if z is not None:
        q  = z[0:int(len(z)/2)] 
    MM = np.zeros((3,3))
    MM[0,0] = p['MM_T'][0,0]+p['M_F']+p['M_RNA']
    MM[0,1] = -p['MM_T'][1,3]+p['L_T']*p['M_RNA']+p['M_F']*p['z_FG']-p['M_RNA']*p['v_yT1c']*p['x_RNAG']*q[2]-p['M_RNA']*p['v_yT1c']*p['z_RNAG']*q[1]*q[2]-p['M_RNA']*p['x_RNAG']*q[1]+p['M_RNA']*p['z_RNAG']-p['M_RNA']*q[1]*q[2]
    MM[0,2] = p['MM_T'][0,6]-p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[2]-p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[1]*q[2]-p['M_RNA']*p['v_yT1c']*p['x_RNAG']*q[1]+p['M_RNA']*p['v_yT1c']*p['z_RNAG']+p['M_RNA']
    MM[1,0] = -p['MM_T'][1,3]+p['L_T']*p['M_RNA']+p['M_F']*p['z_FG']-p['M_RNA']*p['v_yT1c']*p['x_RNAG']*q[2]-p['M_RNA']*p['v_yT1c']*p['z_RNAG']*q[1]*q[2]-p['M_RNA']*p['x_RNAG']*q[1]+p['M_RNA']*p['z_RNAG']-p['M_RNA']*q[1]*q[2]
    MM[1,1] = p['MM_T'][4,4]+p['J_yy_F']+p['J_yy_RNA']+p['L_T']**2*p['M_RNA']-2*p['L_T']*p['M_RNA']*p['v_yT1c']*p['x_RNAG']*q[2]+2*p['L_T']*p['M_RNA']*p['z_RNAG']+p['M_F']*p['z_FG']**2+2*p['M_RNA']*p['v_yT1c']*p['z_RNAG']*q[2]**2+p['M_RNA']*p['x_RNAG']**2+2*p['M_RNA']*p['x_RNAG']*q[2]+p['M_RNA']*p['z_RNAG']**2+p['M_RNA']*q[2]**2
    MM[1,2] = p['MM_T'][6,4]+p['J_yy_RNA']*p['v_yT1c']-p['L_T']*p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[2]+p['L_T']*p['M_RNA']*p['v_yT1c']*p['z_RNAG']+p['L_T']*p['M_RNA']+p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[2]**2+p['M_RNA']*p['v_yT1c']*p['x_RNAG']**2+p['M_RNA']*p['v_yT1c']*p['z_RNAG']**2+p['M_RNA']*p['z_RNAG']
    MM[2,0] = p['MM_T'][0,6]-p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[2]-p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[1]*q[2]-p['M_RNA']*p['v_yT1c']*p['x_RNAG']*q[1]+p['M_RNA']*p['v_yT1c']*p['z_RNAG']+p['M_RNA']
    MM[2,1] = p['MM_T'][6,4]+p['J_yy_RNA']*p['v_yT1c']-p['L_T']*p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[2]+p['L_T']*p['M_RNA']*p['v_yT1c']*p['z_RNAG']+p['L_T']*p['M_RNA']+p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[2]**2+p['M_RNA']*p['v_yT1c']*p['x_RNAG']**2+p['M_RNA']*p['v_yT1c']*p['z_RNAG']**2+p['M_RNA']*p['z_RNAG']
    MM[2,2] = p['MM_T'][6,6]+p['J_yy_RNA']*p['v_yT1c']**2+p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']**2-2*p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[2]+p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']**2+2*p['M_RNA']*p['v_yT1c']*p['z_RNAG']+p['M_RNA']
    return MM

def M_lin(q=None,p=None,z=None):
    """ Linear mass matrix 
    q:  degrees of freedom at operating point, array-like: ['x(t)', 'phi_y(t)', 'q_T1(t)']
    p:  parameters, dictionary with keys: ['J_yy_F', 'J_yy_RNA', 'L_T', 'MM_T', 'M_F', 'M_RNA', 'v_yT1c', 'x_RNAG', 'z_FG', 'z_RNAG']
    """
    if z is not None:
        q  = z[0:int(len(z)/2)] 
    MM = np.zeros((3,3))
    MM[0,0] = p['MM_T'][0,0]+p['M_F']+p['M_RNA']
    MM[0,1] = -p['MM_T'][1,3]+p['M_F']*p['z_FG']-p['M_RNA']*p['v_yT1c']*p['x_RNAG']*q[2]+p['M_RNA']*(p['L_T']+p['z_RNAG'])-q[1]*(p['M_RNA']*p['v_yT1c']*p['z_RNAG']*q[2]+p['M_RNA']*(p['x_RNAG']+q[2]))
    MM[0,2] = p['MM_T'][0,6]-p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[2]+p['M_RNA']*p['v_yT1c']*p['z_RNAG']+p['M_RNA']-q[1]*(p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[2]+p['M_RNA']*p['v_yT1c']*p['x_RNAG'])
    MM[1,0] = -p['MM_T'][1,3]+p['M_F']*p['z_FG']-p['M_RNA']*p['v_yT1c']*p['x_RNAG']*q[2]+p['M_RNA']*(p['L_T']+p['z_RNAG'])-q[1]*(p['M_RNA']*p['v_yT1c']*p['z_RNAG']*q[2]+p['M_RNA']*(p['x_RNAG']+q[2]))
    MM[1,1] = p['MM_T'][4,4]+p['J_yy_F']+p['J_yy_RNA']+p['M_F']*p['z_FG']**2-2*p['M_RNA']*p['v_yT1c']*q[2]*(p['L_T']*p['x_RNAG']-p['z_RNAG']*q[2])+p['M_RNA']*(p['L_T']**2+2*p['L_T']*p['z_RNAG']+p['x_RNAG']**2+2*p['x_RNAG']*q[2]+p['z_RNAG']**2+q[2]**2)
    MM[1,2] = p['MM_T'][6,4]-p['M_RNA']*p['v_yT1c']**2*q[2]*(p['L_T']*p['x_RNAG']-p['z_RNAG']*q[2])+p['M_RNA']*(p['L_T']+p['z_RNAG'])-p['v_yT1c']*(-p['J_yy_RNA']-p['M_RNA']*(p['L_T']*p['z_RNAG']+p['x_RNAG']**2+p['z_RNAG']**2))
    MM[2,0] = p['MM_T'][0,6]-p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[2]+p['M_RNA']*p['v_yT1c']*p['z_RNAG']+p['M_RNA']-q[1]*(p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[2]+p['M_RNA']*p['v_yT1c']*p['x_RNAG'])
    MM[2,1] = p['MM_T'][6,4]-p['M_RNA']*p['v_yT1c']**2*q[2]*(p['L_T']*p['x_RNAG']-p['z_RNAG']*q[2])+p['M_RNA']*(p['L_T']+p['z_RNAG'])-p['v_yT1c']*(-p['J_yy_RNA']-p['M_RNA']*(p['L_T']*p['z_RNAG']+p['x_RNAG']**2+p['z_RNAG']**2))
    MM[2,2] = p['MM_T'][6,6]+2*p['M_RNA']*p['v_yT1c']*p['z_RNAG']+p['M_RNA']-p['v_yT1c']**2*(-p['J_yy_RNA']-p['M_RNA']*(p['x_RNAG']**2-2*p['x_RNAG']*q[2]+p['z_RNAG']**2))
    return MM

def C_lin(q=None,qd=None,p=None,u=None,z=None):
    """ Linear damping matrix 
    q:  degrees of freedom at operating point, array-like: ['x(t)', 'phi_y(t)', 'q_T1(t)']
    qd: dof velocities at operating point, array-like
    p:  parameters, dictionary with keys: ['DD_T', 'L_T', 'MM_T', 'M_F', 'M_RNA', 'v_yT1c', 'x_RNAG', 'z_FG', 'z_RNAG']
    u:  inputs at operating point, dictionary with keys: []
           where each values is a constant!
    """
    if z is not None:
        q  = z[0:int(len(z)/2)] 
        qd = z[int(len(z)/2): ] 
    CC = np.zeros((3,3))
    CC[0,0] = 0
    CC[0,1] = -2*p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*q[2]*qd[2]-p['M_RNA']*p['v_yT1c']*(2*p['x_RNAG']*qd[2]+2*p['z_RNAG']*q[2]*qd[1])-2*p['M_RNA']*p['x_RNAG']*qd[1]-2*p['M_RNA']*q[2]*qd[1]-q[1]*(2*p['MM_T'][0,6]*qd[2]-2*p['MM_T'][1,3]*qd[1]+p['L_T']*p['M_RNA']*qd[1]+2*p['M_F']*p['z_FG']*qd[1]-2*p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*q[2]*qd[2]+2*p['M_RNA']*p['z_RNAG']*qd[1]+p['M_RNA']*(p['L_T']*qd[1]+2*qd[2])+p['v_yT1c']*(-2*p['M_RNA']*p['x_RNAG']*q[2]*qd[1]+2*p['M_RNA']*p['z_RNAG']*qd[2]))
    CC[0,2] = -p['M_RNA']*p['v_yT1c']**2*(2*p['x_RNAG']*qd[2]+2*p['z_RNAG']*q[2]*qd[1])-2*p['M_RNA']*p['v_yT1c']*p['x_RNAG']*qd[1]-q[1]*(2*p['MM_T'][0,6]*qd[1]+p['M_RNA']*p['v_yT1c']**2*(-2*p['x_RNAG']*q[2]*qd[1]+2*p['z_RNAG']*qd[2])+2*p['M_RNA']*p['v_yT1c']*p['z_RNAG']*qd[1]+2*p['M_RNA']*qd[1])
    CC[1,0] = 0
    CC[1,1] = -p['L_T']*p['M_RNA']*p['x_RNAG']*qd[1]-p['L_T']*p['M_RNA']*q[2]*qd[1]-p['M_RNA']*p['v_yT1c']**2*(2*p['L_T']*p['z_RNAG']*q[2]*qd[2]+2*p['x_RNAG']*q[2]**2*qd[2])+p['M_RNA']*p['x_RNAG']*(p['L_T']*qd[1]+2*qd[2])+p['M_RNA']*q[2]*(p['L_T']*qd[1]+2*qd[2])-p['v_yT1c']*(2*p['L_T']*p['M_RNA']*p['x_RNAG']*qd[2]+p['L_T']*p['M_RNA']*p['z_RNAG']*q[2]*qd[1]-2*p['M_RNA']*p['z_RNAG']*q[2]*qd[2]-p['M_RNA']*p['z_RNAG']*q[2]*(p['L_T']*qd[1]+2*qd[2]))
    CC[1,2] = -p['M_RNA']*p['v_yT1c']**2*(2*p['L_T']*p['x_RNAG']*qd[2]+2*p['L_T']*p['z_RNAG']*q[2]*qd[1]+2*p['x_RNAG']*q[2]**2*qd[1]-2*p['z_RNAG']*q[2]*qd[2])+2*p['M_RNA']*p['x_RNAG']*qd[1]+2*p['M_RNA']*q[2]*qd[1]-p['v_yT1c']*(2*p['L_T']*p['M_RNA']*p['x_RNAG']*qd[1]-4*p['M_RNA']*p['z_RNAG']*q[2]*qd[1])
    CC[2,0] = 0
    CC[2,1] = -2*p['M_RNA']*p['x_RNAG']*qd[1]-2*p['M_RNA']*q[2]*qd[1]-p['v_yT1c']**2*(-p['L_T']*p['M_RNA']*p['z_RNAG']*q[2]*qd[1]-2*p['M_RNA']*p['x_RNAG']*q[2]**2*qd[1]+2*p['M_RNA']*p['z_RNAG']*q[2]*qd[2]-p['M_RNA']*p['z_RNAG']*q[2]*(p['L_T']*qd[1]+2*qd[2]))-p['v_yT1c']*(-p['L_T']*p['M_RNA']*p['x_RNAG']*qd[1]+2*p['M_RNA']*p['x_RNAG']*qd[2]-p['M_RNA']*p['x_RNAG']*(p['L_T']*qd[1]+2*qd[2])+4*p['M_RNA']*p['z_RNAG']*q[2]*qd[1])
    CC[2,2] = p['DD_T'][6,6]-2*p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*qd[2]
    return CC

def K_lin(q=None,qd=None,p=None,u=None,z=None):
    """ Linear stiffness matrix 
    q:  degrees of freedom, array-like: ['x(t)', 'phi_y(t)', 'q_T1(t)']
    qd: dof velocities, array-like
    p:  parameters, dictionary with keys: ['KK_T', 'L_T', 'MM_T', 'M_F', 'M_RNA', 'g', 'tilt', 'v_yT1c', 'x_RNAG', 'z_FG', 'z_RNAG']
    u:  inputs at operating point, dictionary with keys: ['T_a']
           where each values is a constant!
    """
    if z is not None:
        q  = z[0:int(len(z)/2)] 
        qd = z[int(len(z)/2): ] 
    KK = np.zeros((3,3))
    KK[0,0] = 0
    KK[0,1] = -2*p['MM_T'][0,6]*qd[1]*qd[2]+p['MM_T'][1,3]*qd[1]**2-p['M_F']*p['z_FG']*qd[1]**2-p['M_RNA']*p['v_yT1c']**2*(-2*p['x_RNAG']*q[2]*qd[1]*qd[2]+p['z_RNAG']*qd[2]**2)-p['M_RNA']*p['z_RNAG']*qd[1]**2-p['M_RNA']*qd[1]*(p['L_T']*qd[1]+2*qd[2])-p['v_yT1c']*(-p['M_RNA']*p['x_RNAG']*q[2]*qd[1]**2+2*p['M_RNA']*p['z_RNAG']*qd[1]*qd[2]-q[2]*u['T_a'])
    KK[0,2] = -2*p['M_RNA']*p['v_yT1c']**2*p['z_RNAG']*qd[1]*qd[2]-p['M_RNA']*p['v_yT1c']*p['z_RNAG']*qd[1]**2-p['M_RNA']*qd[1]**2+p['v_yT1c']*p['tilt']*u['T_a']-q[1]*(-2*p['M_RNA']*p['v_yT1c']**2*p['x_RNAG']*qd[1]*qd[2]+p['v_yT1c']*(-p['M_RNA']*p['x_RNAG']*qd[1]**2-u['T_a']))
    KK[1,0] = 0
    KK[1,1] = p['MM_T'][1,3]*p['g']-p['L_T']*p['M_RNA']*p['g']-p['M_F']*p['g']*p['z_FG']+p['M_RNA']*p['g']*p['v_yT1c']*p['x_RNAG']*q[2]-p['M_RNA']*p['g']*p['z_RNAG']
    KK[1,2] = -p['L_T']*p['M_RNA']*qd[1]**2+p['M_RNA']*p['g']*p['v_yT1c']*p['x_RNAG']*q[1]-p['M_RNA']*p['g']-p['M_RNA']*p['v_yT1c']**2*(2*p['L_T']*p['z_RNAG']*qd[1]*qd[2]+4*p['x_RNAG']*q[2]*qd[1]*qd[2]-p['z_RNAG']*qd[2]**2)+p['M_RNA']*qd[1]*(p['L_T']*qd[1]+2*qd[2])-p['v_yT1c']*(p['L_T']*p['M_RNA']*p['z_RNAG']*qd[1]**2+p['M_RNA']*p['g']*p['z_RNAG']-2*p['M_RNA']*p['z_RNAG']*qd[1]*qd[2]-p['M_RNA']*p['z_RNAG']*qd[1]*(p['L_T']*qd[1]+2*qd[2])+2*q[2]*u['T_a'])-p['tilt']*u['T_a']*(-p['L_T']*p['v_yT1c']+1)
    KK[2,0] = 0
    KK[2,1] = -p['MM_T'][0,6]*p['g']+p['M_RNA']*p['g']*p['v_yT1c']**2*p['x_RNAG']*q[2]-p['M_RNA']*p['g']*p['v_yT1c']*p['z_RNAG']-p['M_RNA']*p['g']
    KK[2,2] = p['KK_T'][6,6]+p['M_RNA']*p['g']*p['v_yT1c']**2*p['x_RNAG']*q[1]-2*p['M_RNA']*p['v_yT1c']*p['z_RNAG']*qd[1]**2-p['M_RNA']*qd[1]**2-p['v_yT1c']**2*(p['M_RNA']*p['g']*p['z_RNAG']-2*p['M_RNA']*p['x_RNAG']*q[2]*qd[1]**2+2*p['M_RNA']*p['z_RNAG']*qd[1]*qd[2]-p['M_RNA']*p['z_RNAG']*qd[1]*(p['L_T']*qd[1]+2*qd[2]))+p['v_yT1c']*p['tilt']*u['T_a']
    return KK

def B_lin(q=None,qd=None,p=None,u=None):
    """ Linear mass matrix 
    q:  degrees of freedom at operating point, array-like: ['x(t)', 'phi_y(t)', 'q_T1(t)']
    qd: dof velocities at operating point, array-like
    p:  parameters, dictionary with keys: ['L_T', 'tilt', 'v_yT1c', 'x_NR', 'z_NR']
    u:  inputs at operating point, dictionary with keys: []
           where each values is a constant!
    The columns of B correspond to:   [T_a(t)]\\ 
    """
    BB = np.zeros((3,1))
    BB[0,0] = -p['v_yT1c']*q[1]*q[2]-p['v_yT1c']*q[2]*p['tilt']+1
    BB[1,0] = p['L_T']+p['v_yT1c']*q[2]**2+p['z_NR']+p['tilt']*(-p['L_T']*p['v_yT1c']*q[2]+p['x_NR']+q[2])
    BB[2,0] = p['v_yT1c']*p['z_NR']+p['v_yT1c']*p['tilt']*(p['x_NR']-q[2])+1
    return BB

