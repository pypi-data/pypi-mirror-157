import PurpleMicroStar.BasicConst as BC
import PurpleMicroStar.BasicMech as BMech
import matplotlib.pyplot as plt
import numpy as np
import pickle as pkl
import math
import os
import prettytable as PT
from tqdm import tqdm

'''
### This module is built for simulating single celestial body, as well as calculating basic properties

@AUTHOR: Yufeng Wang
@DATE: 2022-6
@LICENSE: GPL-V3 license

CopyRight (C) Yufeng-Wang/Airscker, 2022-6

More information about this module please see: https://airscker.github.io/Purple-Micro-Star/
'''

class StarBody():
    '''
    ### Parameters:
    - Position: the position of the planet, in PCI coordinate with the form [x,y,z]
    - Velocity: the velocity of the planet, in PCI coordinate with the form [vx,vy,vz]
    - Mass: the mass of the planet
    - Radius: the radius of the planet
    - Spin: the spin speed of the planet, in rad/s
    - Name: the name of the planet

    All parameters meet SI standard.
    '''
    
    def __init__(self,
                Position=[1,1,1],
                Velocity=[10000,10000,10000],
                Mass=5.965e24,
                Radius=6360e3,
                Spin=[0,0,7.292e-5],
                Name='Earth',
                manybody=[]):
        # Basic properties
        self.pos=np.array(Position)
        self.vel=np.array(Velocity)
        self.mass=Mass
        self.Radius=Radius
        self.spin=np.array(Spin)
        self.name=Name
        self.rho=3*self.mass/(4*math.pi*self.Radius**3)
        self.force=np.array([0.0,0.0,0.0])
        # self.Sphere=self.SphereModel()
        self.Sphere=None
        self.iter=0
        self.Ctime=0
        # Advanced properties
        self.ad_prop={
            'V1':math.sqrt(BC.G*self.mass/self.Radius),
            'V2':math.sqrt(2*BC.G*self.mass/self.Radius),
            'Roche_limit':0,
            'Black_hole':bool(self.Radius<=BC.G*self.mass/BC.c**2),
            'Vision_radius':BC.G*self.mass/BC.c**2,
            'Max_spin':math.sqrt(BC.G*self.mass/(self.Radius**3))
        }
        if manybody!=[]:
            self.Force(manybody)
            self.Roche_limit(manybody)
        # Other parameters
        self.DAngle=1
    def __str__(self):
        str1='---Basic Information of the StarBody {}---\n'.format(self.name)
        str2=PT.PrettyTable()
        str2.field_names=['Properties','Value']
        str2.add_rows([['Position(m)',self.pos],
                        ['Velocity(m/s)',self.vel],
                        ['Mass(kg)',self.mass],
                        ['Density(kg/m3)',self.rho],
                        ['Radius(m)',self.Radius],
                        ['Spin Velocity(rad/s)',self.spin],
                        ['Gravity Force(N)',self.force],
                        ['Time Since Launch(s)',self.Ctime],
                        ['Iteration Times',self.iter]])
        print(str1)
        print(str2)
        str3='\n---Advanced Properties of the StarBody {}---\n'.format(self.name)
        str4=PT.PrettyTable()
        str4.field_names=['Properties','Value']
        str4.add_rows([['1st order velocity(m/s)',self.ad_prop['V1']],
                        ['2nd order velocity(m/s)',self.ad_prop['V2']],
                        ['Roche limit proportion',self.ad_prop['Roche_limit']/self.mass],
                        ['Black Hole',self.ad_prop['Black_hole']],
                        ['Vision Radius(m)',self.ad_prop['Vision_radius']],
                        ['Maximum Spin Velocity(rad/s)',self.ad_prop['Max_spin']]])
        print(str3)
        print(str4)
        # str5=('\n---Sphere Model Properties of the StarBody {}---\n'.format(self.name))
        # str6=PT.PrettyTable()
        # str6.field_names=['Properties','Value']
        # str6.add_rows([['Sphere Model Data shape',self.Sphere.shape],
        #                 ['2nd-Index of the Sphere Center Plane',(self.Sphere.shape[1]-1)/2],
        #                 ['Segmentation D_Angle(degree)',self.DAngle],
        #                 ['Outer Sphere Radius(m)',self.Radius]])
        # print(str5)
        # print(str6)
        if self.ad_prop['Roche_limit']/self.mass>=1:
            print('\n---Starbody {} Crashed, RocheLimit {}(kg) Reached---\n'.format(self.name,self.ad_prop['Roche_limit']))
        str7='---More are available because of your exploration! And all properties meet SI standard---\n'
        
        return str7
    def Force(self,manybody=[]):
        '''
        ## Get the gravity force of this planet(Multibody gravity force)
        ### Parameter:
            manybody: the list of other existing planet bodies' Object of StarBody
        ### Return:
            The Multibody gravity force of this planet
        '''
        try:
            for i in range(len(manybody)):
                self.force+=BMech.G_Force(self.mass,manybody[i].mass,self.pos,manybody[i].pos)
        except:
            print('Force Calculation Error!')
            return None
        return self.force
    def Iteration(self,dt=0.001,iterCount=1):
        '''
        ## Get the motion information of this planet at specified time
        ### Parameters:
        - dt: the time period per motion used
        - iterCount: the iteration times of dt
        '''
        iterCount=int(iterCount)
        if self.ad_prop['Roche_limit']/self.mass<1:
            self.iter+=iterCount
            self.Ctime+=iterCount*dt
            try:
                for i in range(iterCount):
                    self.pos=self.vel*dt+self.pos+self.force*dt**2/(2*self.mass)
                    self.vel=self.vel+self.force*dt/self.mass
            except:
                print('Iteration error!')
                return None
            return 0
        else:
            return 0
    def Roche_limit(self,manybody=[]):
        '''
        ## Get all starbodies' roche limit proportion
        '''
        sum=0
        for i in range(len(manybody)):
            sum+=(manybody[i].mass*2*self.Radius**3)/(math.sqrt(np.sum(self.pos-manybody[i].pos)**2))**3
        self.ad_prop['Roche_limit']=sum
        return sum
    def __SphereModel(self,DAngle=0.1):
        '''
        ### Parameters:
        - DAngle: the angle between nearby points
        - DR: the distance between nearby spheres
        - output: the folder to save the sphere data file

        ### Return:
        - Normalized Sphere Model\n
            Shape of data: (2,NumberOfPlanes,DividedPatten)
            -- 2: X/Y axis
            -- NumberOfPlanes: Number of Image Planes (DAngle=1 -> 90*2+1)
            -- DividedPatten: 360/DAngle
            
        This function gives us with a outer sphere model, when we want to build whole ball model we just need to multiply 1/proportion to get the inner sphere model
        '''
        X=[]
        Y=[]
        self.DAngle=DAngle
        bar=tqdm(range(int(90.0/DAngle+1)),mininterval=1)
        bar.set_description('Building Sphere Star Model of {}'.format(self.name))
        for i in bar:
            x=self.Radius*np.cos(np.deg2rad(i*DAngle))*np.cos(np.deg2rad(np.arange(0,360,DAngle)))
            y=self.Radius*np.cos(np.deg2rad(i*DAngle))*np.sin(np.deg2rad(np.arange(0,360,DAngle)))
            X.append(x)
            Y.append(y)
            if i!=0:
                X.insert(0,x)
                Y.insert(0,-y)
        self.Sphere=np.array([X,Y])
        return self.Sphere
    def __SaveSphereModel(self,output=''):
        if output!='':
            try:
                os.makedirs(output)
            except:
                pass
            print('---Saving StarBody Sphere Model---')
            path='{}\\SphereModel_R_{}_DAngle_{}.pkl'.format(output,self.Radius,self.DAngle)
            file=open(path,'wb')
            pkl.dump(self.Sphere,file)
            print('---Sphere Model Data Saved as {}---'.format(path))
        return path



