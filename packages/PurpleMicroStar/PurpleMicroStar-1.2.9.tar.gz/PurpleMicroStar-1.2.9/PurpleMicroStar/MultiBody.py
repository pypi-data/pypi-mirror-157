import math
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
import numpy as np
import pandas as pd
import os
import csv
# import pyqtgraph as pg
import pickle
import PurpleMicroStar.BasicConst as BC
import PurpleMicroStar.BasicMech as BMech
import PurpleMicroStar.StarBody as Sbody
from prettytable import PrettyTable

'''
### This module is built for Multibody motion simulation

@AUTHOR: Yufeng Wang
@DATE: 2022-6
@LICENSE: GPL-V3 license

CopyRight (C) Yufeng-Wang/Airscker, 2022-6

More information about this module please see: https://airscker.github.io/Purple-Micro-Star/
'''

class MultiBody:
    '''
    ## Buid a cluster of planets, allow they evolution via time and store their Astrophysics properties
    ### Parameter:
        manybody: a list of Starbody Objects

    ### Optional operation:
        You can build your new cluster via Dataset(), more information please refer to function Dataset()

        And you can rebuild your former cluster stored in some files, more information please refer to function Rebuild()
    '''
    def __init__(self,manybody=[]):
        self.mbody=manybody
        self.data=None
        self.pos_data=None
        self.vel_data=None
        self.Crashed=[]
    def __str__(self):
        str1='\n---Basic Information of Multibody---\n'
        str2='\n{}'.format(self.data)
        # str3=''
        return str1+str2
    def Iteration(self,dt=0.001,iterCount=100000,output='.\\Curve_data'):
        '''
        ## Calculate all planets' motion properties, as well as their body properties, then save them into files
        ### Parameters:
        - dt: the time period per motion used
        - iterCount: the iteration times of dt

        ### Return:
        - Pos_curve: The position information of every planet in every iterated time, in the form of nparray\n
                [[[p1_t1],[p2_t1],[p3_t1]],
                 [[p1_t2],[p2_t2],[p3_t2]],...],shape=(iter,body_num,3)
        - Vel_curve: The velocity information of every planet in every iterated time, in the form of nparray\n
                [[[v1_t1],[v2_t1],[v3_t1]],
                 [[v1_t2],[v2_t2],[v3_t2]],...]
        '''
        iterCount=int(iterCount)
        print('\n---Total time of motion: {}s, total iteration times: {}---\n'.format(iterCount*dt,iterCount))
        Pos_curve=[]
        Vel_curve=[]
        bar=tqdm(range(iterCount),mininterval=1)
        bar.set_description('Calculating Multibody Motion Properties')
        mbody=self.mbody.copy()
        for iter in bar:
            # Calculate their gravity force and roche_limit
            for i in range(len(mbody)):
                mcopy=mbody.copy()
                mcopy.pop(i)
                mbody[i].Force(mcopy)
                mbody[i].Roche_limit(mcopy)
                
            # Delete Crashed Starbody
            for i in range(len(mbody)):
                if mbody[i].ad_prop['Roche_limit']/mbody[i].mass>=1:
                    self.Crashed.append(mbody[i])
                    print('---StarBody *{}* Crashed at Iteration *{}*---'.format(mbody[i].name,iter))
                    mbody.pop(i)
                    break

            # Iterate their motion information
            for i in range(len(mbody)):
                mbody[i].Iteration(dt=dt,iterCount=1)

            # Store body data
            for i in range(len(mbody)):
                self.mbody[self.mbody.index(mbody[i])]=mbody[i]

            # Get pos/vel curve data
            Pos_curve.append([0]*len(self.mbody))
            Vel_curve.append([0]*len(self.mbody))
            for i in range(len(self.mbody)):
                Pos_curve[iter][i]=self.mbody[i].pos
                Vel_curve[iter][i]=self.mbody[i].vel
        
        # Prepare for data saving
        Pos_curve=np.array(Pos_curve)
        Vel_curve=np.array(Vel_curve)
        # Save curve data
        try:
            os.makedirs(output)
        except:
            pass
        # Save body basic information
        with open('{}\\Multibody_{}_Iter_{}_dt_{}_body_Rebuild.csv'.format(output,len(self.mbody),iterCount,dt),'w',newline='')as f:
            csv_writer=csv.writer(f)
            csv_writer.writerow(['Name','Mass','Radius','sx','sy','sz'])
            for i in range(len(self.mbody)):
                csv_writer.writerow([self.mbody[i].name,self.mbody[i].mass,self.mbody[i].Radius,self.mbody[i].spin[0],self.mbody[i].spin[1],self.mbody[i].spin[2]])
        f.close()
        # # Save iteration image
        # plt.imsave('{}\\Multibody_{}_Iter_{}_Position.jpg'.format(output,len(self.mbody),iterCount),pos_norm)
        # plt.imsave('{}\\Multibody_{}_Iter_{}_Velocity.jpg'.format(output,len(self.mbody),iterCount),vel_norm)
        # Save position and velocity data
        with open('{}\\Multibody_{}_Iter_{}_dt_{}_Position.pkl'.format(output,len(self.mbody),iterCount,dt),'wb')as f:
            pickle.dump(Pos_curve,f)
        f.close()
        with open('{}\\Multibody_{}_Iter_{}_dt_{}_Velocity.pkl'.format(output,len(self.mbody),iterCount,dt),'wb')as f:
            pickle.dump(Vel_curve,f)
        f.close()

        print('\n---Iteration over, all data saved---\n')
        self.pos_data=Pos_curve
        self.vel_data=Vel_curve

        
        if self.Crashed!=[]:
            print('\n---StarBody Crashed are listed here---\n')
            str1=PrettyTable()
            str1.field_names=['StarBody Name','Roche Limit','Iteration Times']
            for i in range(len(self.Crashed)):
                str1.add_row([self.Crashed[i].name,self.Crashed[i].ad_prop['Roche_limit'],self.Crashed[i].iter])
            print(str1)
        return Pos_curve,Vel_curve
    def Dataset(self,datapath='.\\exampledata\\Multibody.csv',datasep=','):
        '''
        ## Load MultiBody From Given formated Dataset .csv file
        ### Parameters:
        - datapath: the csv data root path of planets' basic data
        - datasep: the seperation of every information

        ### Columns' name:  
            Name,x,y,z,vx,vy,vz,Mass,Radius,Spinx,Spiny,Spinz\n
            If you don't obey this rule, the result may boom

        ### Return:
            The list of Object 'Starbody'
        '''
        # read data
        try:
            self.data=pd.read_csv(datapath,sep=datasep)
        except:
            print('\n---No MultiBody data read, Check the data file path!---\n')
            exit()
            # return None,None
        body=[]
        # create starbody objects
        try:
            for i in range(self.data.shape[0]):
                body.append(Sbody.StarBody(Position=[self.data.iloc[i][1],self.data.iloc[i][2],self.data.iloc[i][3]],
                                    Velocity=[self.data.iloc[i][4],self.data.iloc[i][5],self.data.iloc[i][6]],
                                    Mass=self.data.iloc[i][7],
                                    Radius=self.data.iloc[i][8],
                                    Spin=[self.data.iloc[i][9],self.data.iloc[i][10],self.data.iloc[i][11]],
                                    Name=self.data.iloc[i][0]))
            self.mbody=body.copy()
        except:
            print('Check the sep or column format of data!')
            return None,None
        # Initailize their basic information
        for i in range(len(self.mbody)):
            mcopy=self.mbody.copy()
            mcopy.pop(i)
            self.mbody[i].Force(mcopy)
            self.mbody[i].Roche_limit(mcopy)
        return self.mbody,self.data
    def Rebuild(self,body='.\\exampledata\\Curve_data\\Multibody_3_Iter_100_dt_10_body_Rebuild.csv',
                position='.\\exampledata\\Curve_data\\Multibody_3_Iter_100_dt_10_Position.pkl',
                velocity='.\\exampledata\\Curve_data\\Multibody_3_Iter_100_dt_10_Velocity.pkl'):
        '''
        ## Rebuild your planet cluster using data files saved by Iteration(), make sure you haven't changed anything of these data, you just need to find the cooresponding filenames
        ### Parameters:
        - body: the $body_Rebuild.csv path
        - position: the $Position.csv path
        - Velocity: the $Velocity.csv path
        ### Return:
        - The list of position curve data, The list of the velocity curve data, The list of Object 
        '''
        # Get basic body info
        body_data=pd.read_csv(body)
        body_name=body_data['Name']
        body_mass=body_data['Mass']
        body_radius=body_data['Radius']
        body_spinx=body_data['sx']
        body_spiny=body_data['sy']
        body_spinz=body_data['sz']
        # Get position and velocity data
        with open(position,'rb')as f:
            pos_data=pickle.load(f)
        f.close()
        with open(velocity,'rb')as f:
            vel_data=pickle.load(f)
        f.close()

        # Rebuild Starbody Object cluster
        manybody=[]
        for i in range(len(body_name)):
            manybody.append(Sbody.StarBody(Position=pos_data[-1][i],Velocity=vel_data[-1][i],Mass=body_mass[i],Radius=body_radius[i],Spin=[body_spinx[i],body_spiny[i],body_spinz[i]],Name=body_name[i]))
        for i in range(len(manybody)):
            m_copy=manybody.copy()
            m_copy.pop(i)
            manybody[i].Force(m_copy)
        self.mbody=manybody
        self.pos_data=pos_data
        self.vel_data=vel_data
        return pos_data,vel_data,manybody
    def Plot(self):
        '''
        ## Plot the motion curve of Multibodies
        '''
        print('---Plotting motion curve of Multibodies---')
        body_x=[]
        body_y=[]
        body_z=[]
        try:
            for i in range(self.pos_data.shape[1]):
                body_x.append([])
                body_y.append([])
                body_z.append([])
                for j in range(self.pos_data.shape[0]):
                    body_x[i].append(self.pos_data[j][i][0])
                    body_y[i].append(self.pos_data[j][i][1])
                    body_z[i].append(self.pos_data[j][i][2])
        except:
            print('---Iteration need to done before Plotting---')
            return None
        body_x=np.array(body_x)
        body_y=np.array(body_y)
        body_z=np.array(body_z)
        # Plot static image
        figure=plt.figure()
        ax=Axes3D(figure,auto_add_to_figure=False)
        figure.add_axes(ax)
        ax.set_title('Motion curve of Multibodies')
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        # figure.colorbar(mpl.cm.ScalarMappable())
        for i in range(len(body_x)):
            ax.plot3D(body_x[i],body_y[i],body_z[i],label=self.mbody[i].name)
        for i in range(self.pos_data[-1].shape[0]):
            ax.scatter3D(self.pos_data[-1][i][0],self.pos_data[-1][i][1],self.pos_data[-1][i][2],s=200*self.mbody[i].Radius/BC.R_earth)
        label=[]
        ax.legend()
        plt.show()
        return [body_x,body_y,body_z]

            


    
