import numpy as np
import PurpleMicroStar.BasicConst as BC
'''
### This module contains some basic mathematical and physical algorithms

@AUTHOR: Yufeng Wang
@DATE: 2022-6
@LICENSE: GPL-V3 license

CopyRight (C) Yufeng-Wang/Airscker, 2022-6

More information about this module please see: https://airscker.github.io/Purple-Micro-Star/
'''

def G_Force(m1=1,m2=1,pos1=[0,0,0],pos2=[1,1,1]):
    '''
    ## Get two planets' gravity force
    ### Parameters:
    - m1,m2: the mass of two planets
    - pos1,pos2: the PCI coordinate position of two planets, in the form of list [x,y,z]
    ### Return:
    - The gravity force of two planet, in the form of nparray [fx,fy,fz]
    - If two planets too close to get result, None is returned
    '''
    pos1=np.array(pos1)
    pos2=np.array(pos2)
    rel_pos=np.sqrt(np.sum((pos2-pos1)**2))
    if rel_pos!=0:
        output=(pos2-pos1)*BC.G*m1*m2/rel_pos**3
    else:
        print('Position corrupted!')
        return None
    return output

def Vec_Project(vec1=[1,0,0],vec2=[1,1,1]):
    '''
    ## Project the 2nd vector to 1st vector
    ### Parameters:
    - vec1: the vector selected as base, in the form of list [x,y,z]
    - vec2: the vector need to be projected, in the form of list [x,y,z]
    ### Return:
        the projected vector, in the form of nparray [x,y,z]
    '''
    vec1=np.array(vec1)
    vec2=np.array(vec2)
    output=np.dot(vec1,vec2)*vec1/np.sum(vec1**2)
    return output

def Vec_Angle(vec1=[1,0,0],vec2=[1,1,1]):
    '''
    ## Get two vectors' angle
    ### Parameters:
        vec1,vec2: Vectors, in the form of list [x,y,z]
    ### Return:
        The angle of two vectors, in degree
    '''
    vec1=np.array(vec1)
    vec2=np.array(vec2)
    output=np.rad2deg(np.arccos(np.dot(vec1,vec2)/(Vec_Length(vec1)*Vec_Length(vec2))))
    return output

def AngleXYZ(vec,plane='XY'):
    '''
    ## Get the angle between the vector and specified plane
    ### Parameters:
        plane: XY,YZ,XZ available
    ### Return:
        The angle in degree
    '''
    vec_c=vec.copy()
    plus=1
    if plane=='XY':
        vec_c[0]=0
        if vec[2]<0:
            plus=-1
        return plus*(90-Vec_Angle(vec_c,[0,0,1]))
    if plane=='XZ':
        vec_c[0]=0
        if vec[1]<0:
            plus=-1
        return plus*(90-Vec_Angle(vec_c,[0,1,0]))
    if plane=='YZ':
        vec_c[0]=0
        if vec[0]<0:
            plus=-1
        return plus*(90-Vec_Angle(vec_c,[1,0,0]))

def Vec_Length(vec=[1,1,1]):
    '''
    ## Get the length of vector
    '''
    vec=np.array(vec)
    return np.sqrt(np.sum(vec**2))

def Vec_Norm(vec=[10,6,8]):
    '''
    ## Get normalized vector
    '''
    return vec/Vec_Length(vec)

def Rotate_XYZ(vec=[1,1,-1],rad=0.1,Axis='X'):
    '''
    ## Rotate vector clockwise
    '''
    if Axis=='X':
        Rotate=np.array([[1,0,0],[0,np.cos(rad),-np.sin(rad)],[0,np.sin(rad),np.cos(rad)]])
    if Axis=='Y':
        Rotate=np.array([[np.cos(rad),0,np.sin(rad)],[0,1,0],[-np.sin(rad),0,np.cos(rad)]])
    if Axis=='Z':
        Rotate=np.array([[np.cos(rad),-np.sin(rad),0],[np.sin(rad),np.cos(rad),0],[0,0,1]])

    return np.dot(Rotate,np.array(vec))
