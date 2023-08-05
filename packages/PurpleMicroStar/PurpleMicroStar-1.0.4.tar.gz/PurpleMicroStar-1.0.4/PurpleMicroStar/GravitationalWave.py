'''
# Gravitational Wave Simulator
Every massive object that accelerates produces gravitational waves.This includes humans, cars, airplanes etc., 
but the masses and accelerations of objects on Earth are far too small to make gravitational waves big enough to detect with our instruments.
To find big enough gravitational waves, we have to look far outside of our own solar system.

It turns out that the Universe is filled with incredibly massive objects that undergo rapid accelerations that by their nature,
generate gravitational waves that we can actually detect. Examples of such things are orbiting pairs of black holes and neutron stars,
or massive stars blowing up at the ends of their lives.

LIGO scientists have defined four categories of gravitational waves based on what generates them:
- Continuous
- Compact Binary Inspiral
- Stochastic
- Burst

Each category of objects generates a unique or characteristic set of signal that interferometers can sense,
but not all types of Gravitational Wave can be simulated numerically. This module simulate the gravitational wave of *Compact Binary Inspiral Gravitational Wave* and *Continuous Gravitational Wave*

More information about this please see: https://www.ligo.caltech.edu/page/gw-sources

@AUTHOR: Yufeng Wang
@DATE: 2022-6
@LICENSE: GPL-V3 license

CopyRight (C) Yufeng-Wang/Airscker, 2022-6

More information about this module please see: https://airscker.github.io/Purple-Micro-Star/
'''
import pickle as pkl
import PurpleMicroStar.MultiBody as MB
import PurpleMicroStar.StarBody as SB
import PurpleMicroStar.BasicConst as BC
import PurpleMicroStar.BasicMech as BMech
import numpy as np
import math
import prettytable as PT
import matplotlib.pyplot as plt
import os
from tqdm import tqdm


N=32/5

class CBIGW:
    '''
    # Compact Binary Inspiral Gravitational Waves\n
    Compact binary inspiral gravitational waves are produced by orbiting pairs of massive and dense ("compact") objects like white dwarf stars, black holes, and neutron stars.\n
    There are three subclasses of "compact binary" systems in this category of gravitational-wave generators:
    - Binary Neutron Star (BNS)
    - Binary Black Hole (BBH)
    - Neutron Star-Black Hole Binary (NSBH)
    
    Each binary pair creates a unique pattern of gravitational waves, but the mechanism of wave-generation is the same across all three. It is called "inspiral".

    Inspiral occurs over millions of years as pairs of dense compact objects revolve around each other.
    As they orbit, they emit gravitational waves that carry away some of the system's orbital energy.
    As a result, over eons, the objects orbit closer and closer together.
    Unfortunately, moving closer causes them to orbit each other faster, which causes them to emit stronger gravitational waves,
    which causes them to lose more orbital energy, inch ever closer, orbit faster, lose more energy, move closer, orbit faster... etc.
    The objects are doomed, inescapably locked in a runaway accelerating spiraling embrace.

    ### Parameters:\n
    - m1,m2: The mass of planets\n
    - r1,r2: The orbit radius of per planets\n
    - Name: the name of binary planets\n
    '''
    def __init__(self,m1=2e2*BC.M_sun,m2=1e3*BC.M_sun,r1=1e-5*BC.AU,r2=2e-5*BC.AU,Name='CBIG_SYS1'):
        self.name=Name
        self.M=np.array([m1,m2])
        self.r_int=np.array([r1,r2])
        self.r=np.array([r1,r2])
        self.spin=Orbit_spin(self.M[0],self.M[1],np.sum(self.r_int))
        self.info1={'Name of Black Holes':['BlackHole1','BlackHole2'],'Mass of Black Holes':[m1,m2],'Initial Orbit Radius':[r1,r2],}
        self.Coalescence_time=np.sum(self.M)*np.sum(self.r_int)**4/(N*Reduce_mass(self.M[0],self.M[1])*Schwarz_Radius(np.sum(self.M))**3*BC.c)
        self.Cu_time=0
    def __str__(self):
        str1='\n---Basic information of Binary Black Hole System---\n\n'
        str2=PT.PrettyTable()
        str2.field_names=['Name of Planets','Mass of Planets(M_Sun)','Initial Orbit Radius(AU)']
        str2.add_rows([['Black Hole 1',self.M[0]/BC.M_sun,self.r_int[0]/BC.AU],['Black Hole 2',self.M[1]/BC.M_sun,self.r_int[1]/BC.AU]])
        print(str1,str2,'\n')
        str3='Total coalescence time: {}s\nCurrent time of the system: {}s\n'.format(self.Coalescence_time,self.Cu_time)
        str4='\n---More Properties are waiting for your exploration!---\n'
        return str3+str4
    def Grav_Wave(self,Obser_R=[1e3,1e3,1e3],T_now=200):
        '''
        ## Get the gravitational wave field
        ### Parameters:
        - Obser_R: the position vector of the observer
        - T_now: the time at the place of observation
        
        ### Return:
            The Gravitational Wave Field
        '''
        if T_now>self.Coalescence_time:
            print('---Coalescence Time {}s Reached!, Current Time: {}s---'.format(self.Coalescence_time,T_now))
            return 0
        # Basic args
        cu_r=self.Distance(T_now=T_now)
        mu=Reduce_mass(self.M[0],self.M[1])
        spin=Orbit_spin(self.M[0],self.M[1],cu_r)
        theta=np.deg2rad(BMech.Vec_Angle(Obser_R,[0,0,1]))
        t_r=T_now-BMech.Vec_Length(Obser_R)/BC.c
        R_len=BMech.Vec_Length(Obser_R)
        # Calculation
        coef=BC.G*mu*spin**3*cu_r**2/(2*BC.c**3*R_len)
        # field_x=np.sin(2*theta)*np.sin(2*spin*t_r)*np.cos(theta)*np.cos(spin*t_r)+2*np.sin(theta)*np.cos(2*spin*t_r)*np.sin(spin*t_r)
        # fiels_y=np.sin(2*theta)*np.sin(2*spin*t_r)*np.cos(theta)*np.sin(spin*t_r)-2*np.sin(theta)*np.cos(2*spin*t_r)*np.cos(spin*t_r)
        # field_z=-np.sin(theta)
        field_x=np.sin(2*theta)*np.sin(2*spin*t_r)*np.cos(theta)+2*np.sin(theta)*np.cos(2*spin*t_r)
        fiels_y=np.sin(2*theta)*np.sin(2*spin*t_r)*np.cos(theta)-2*np.sin(theta)*np.cos(2*spin*t_r)
        field_z=-np.sin(theta)
        field=np.array([field_x,fiels_y,field_z])
        # Set properties
        self.Cu_time=T_now
        self.spin=spin
        return coef*field
    def Distance(self,T_now=200):
        '''
        ## Get the distance of balckholes at specified time
        '''
        if T_now>self.Coalescence_time:
            print('---Coalescence Time {}s Reached!, Current Time: {}s---'.format(self.Coalescence_time,T_now))
            return 0
        cu_r=math.pow((np.sum(self.r_int)**4-(N*(Reduce_mass(self.M[0],self.M[1])/np.sum(self.M))*BC.c*T_now*Schwarz_Radius(np.sum(self.M))**3)),1/4)
        self.r[0]=cu_r*self.M[1]/(np.sum(self.M))
        self.r[1]=cu_r*self.M[0]/(np.sum(self.M))
        self.Cu_time=T_now
        return cu_r
    def DEnergy_Loss(self,T_now=200):
        '''
        ## Get the derivation of the total energy of starbodies at specified time
        '''
        if T_now>self.Coalescence_time:
            print('---Coalescence Time {}s Reached!, Current Time: {}s---'.format(self.Coalescence_time,T_now))
            return 0
        Reduced_mass=Reduce_mass(self.M[0],self.M[1])
        Distance=self.Distance(T_now)
        Orbit_Spin=Orbit_spin(self.M[0],self.M[1],Distance)
        return N*(BC.G*Reduced_mass**2*Distance**4*Orbit_Spin**6)/(BC.c**5)
    def Detect_Signal(self,Obser_R=[1e3,1e3,1e3],T_now=200):
        '''
        ## Get the interferometer strain signal of LIGO\n
        ### Parameters:
        - Obser_R: the position vector of the observer
        - T_now: the time at the place of observation
        
        ### Return:
            The Detected Gravitational Wave Field Signal(scalar)
        '''
        if T_now>self.Coalescence_time:
            print('---Coalescence Time {}s Reached!, Current Time: {}s---'.format(self.Coalescence_time,T_now))
            return 0
        coef=Reduce_mass(self.M[0],self.M[1])/(8*np.sum(self.M))
        r=self.Distance(T_now)
        spin=Orbit_spin(self.M[0],self.M[1],r)
        coef*=Schwarz_Radius(np.sum(self.M))**2/(r*BMech.Vec_Length(Obser_R))
        theta=BMech.Vec_Angle(Obser_R,[0,0,1])
        # beta=np.arcsin(np.cos(theta)*np.cos(spin*T_now))
        beta=np.arcsin(np.cos(theta))
        coef*=np.sin(beta)*np.cos(beta)*np.sin(2*theta)*np.cos(2*spin*T_now)
        return coef

    def Orbit_Phase(self,T_now=200):
        '''
        ## Get the r1/r2 phase at the specified time, phase=0 when r1 along the x+ axis
        '''
        if T_now<self.Coalescence_time:
            tsc=2*BC.G*np.sum(self.M)*math.pow(Reduce_mass(self.M[0],self.M[1])/np.sum(self.M),3/5)/BC.c**3
            phase=math.pow(0.4,5/8)*(math.pow(self.Coalescence_time/tsc,5/8)-math.pow((self.Coalescence_time-T_now)/tsc,5/8))
            return phase
        else:
            print('---Coalescence Time {}s Reached!, Current Time: {}s---'.format(self.Coalescence_time,T_now))
            return 0
    def DATA(self,Dt=0.1,T_init=0,T_end=10,Obser_R=[1e3,1e3,1e3],imgoutput='',Plot=True):
        '''
        ## Plot data of Gravitational wave
        ### Parameters:
        - Dt: the time interval between nearby points
        - T_init: the start time of data
        - T_end: the end time of data
        - Obser_R: the position vector of the observer
        - imgoutput: the folder to save the ploted image, if it's empty, no image will be saved
        - Plot: plot the data curve
        '''
        # Prepare the data
        dis=[]
        grav=[]
        signal=[]
        phase=[]
        if T_end>self.Coalescence_time:
            print('---Coalescence Time {}s Reached!, Current End Time: {}s---'.format(self.Coalescence_time,T_end))
            return 0
        if T_init>=T_end:
            print('Start time {}s is larger than End time {}s!'.format(T_init,T_end))
            return 0

        # Calculate
        time=range(1+int((T_end-T_init)/Dt))
        bar=tqdm(time,mininterval=1)
        bar.set_description('Calculating Gravitational Wave Data')
        for i in bar:
            dis.append(self.Distance(T_now=T_init+i*Dt))
            grav.append(BMech.Vec_Length(self.Grav_Wave(Obser_R=Obser_R,T_now=T_init+i*Dt)))
            signal.append(self.Detect_Signal(Obser_R=Obser_R,T_now=T_init+i*Dt))
            phase.append(np.sin(self.Orbit_Phase(T_now=T_init+i*Dt)))
        time=np.array(time)
        time=time*Dt+T_init
        dis=np.array(dis)
        grav=np.array(grav)
        signal=np.array(signal)
        phase=np.array(phase)
        
        # Plot data
        plt.figure(figsize=(30,20))
        plt.subplot(221)
        plt.plot(time,dis)
        plt.title('Distance between the binary planets')
        plt.xlabel('Time/s')
        plt.ylabel('Distance/m')
        
        plt.subplot(222)
        plt.plot(time,grav)
        plt.title('Strength of the gravitatioanl wave')
        plt.xlabel('Time/s')
        plt.ylabel('Gravitatioanl wave strength')

        plt.subplot(223)
        plt.plot(time,signal)
        plt.title('Signal strength detected by laser interferomater')
        plt.xlabel('Time/s')
        plt.ylabel('Signal Strength')

        plt.subplot(224)
        plt.plot(time,phase)
        plt.title('Orbit pahse of the binary planets')
        plt.xlabel('Time/s')
        plt.ylabel('Phase/sin()')
        
        # save the data fig
        if imgoutput!='':
            try:
                os.makedirs(imgoutput)
            except:
                pass
            path=os.path.join(imgoutput,'{}_Ti_{}_Te_{}_Dt_{}_Obser_{}.jpg'.format(self.name,T_init,T_end,Dt,Obser_R))
            plt.savefig(path)
            print('---Data image saved as {}---'.format(path))
        # Show the image
        if Plot==True:
            plt.show()# DONOT put plt.show() in front of plt.savefig!!!
        return dis,grav,signal,phase
    def __SaveData(self,Dt=0.1,T_init=0,T_end=10,Obser_R=[1e3,1e3,1e3],output=''):
        # # save the data
        # if output!='':
        #     try:
        #         os.makedirs(output)
        #     except:
        #         pass
        #     path=os.path.join(output,'{}_Ti_{}_Te_{}_Dt_{}_Obser_{}.pkl'.format(self.name,T_init,T_end,Dt,Obser_R))
        #     with open(path,'wb')as f:
        #         pkl.dump('data',f)
        #     print('---Data saved as {}---'.format(path))
        pass

class CGW(SB.StarBody):
    '''
    # Continuous gravitational waves
    Continuous gravitational waves are thought to be produced by a single spinning massive object like a neutron star. 
    Any bumps on or imperfections in the spherical shape of this star will generate gravitational waves as it spins. 
    If the spin-rate of the star stays constant, so too are the gravitational waves it emits. 
    That is, the gravitational wave is continuously the same frequency and amplitude (like a singer holding a single note). 
    That's why these are called “Continuous Gravitational Waves”.
    ### Parameters:
    - Mass: the mass of the pulsar
    - Radius: the radius of the pulsar
    - Spin: the saclar spin speed of the planet, in rad/s, the spin will be automatically aligned to z-axis
    - Name: the name of the pulsar
    - Meg: the megnatic dipole of the pulsar
    - RotI: the rotation inertia of the pulsar

    All parameters meet SI standard.
    '''
    def __init__(self,Name='PulsarAX01',Mass=1e5*BC.M_sun,Radius=1e-3*BC.R_earth,Spin=1,Meg=[1e3,1e3,1e3],RotI=[1.1,0.9,1.2]):
        super().__init__(Position=[0,0,0],Velocity=[0,0,0],Mass=Mass,Radius=Radius,Spin=[0,0,Spin],Name=Name)
        if BMech.Vec_Length(self.spin)>self.ad_prop['Max_spin']:
            self.spin=self.ad_prop['Max_spin']
            print('---Spin Velocity Boomed, Refreshed as the Maximum Value---')
        self.MegDio=np.array(Meg)
        self.MegSur=BC.mu0*self.MegDio/(2*math.pi*self.Radius**3)
        self.RotI=2*self.mass*self.Radius**2/5*np.array(RotI)
    def __str__(self):
        str1='---Basic Information of the Fast Spinning Starbody {}---\n'.format(self.name)
        str2=PT.PrettyTable()
        str2.field_names=['Properties','Value']
        str2.add_rows([['Mass(kg)',self.mass],
                        ['Density(kg/m3)',self.rho],
                        ['Radius(m)',self.Radius],
                        ['Spin Velocity(rad/s)',self.spin],
                        ['Magnetic Dipole(A.m2)',self.MegDio],
                        ['Surface Megnatic Field(T)',self.MegSur],
                        ['The moment of inertia(kg.m2)',self.RotI]])
        print(str1)
        print(str2)
        str3='\n---Advanced Properties of the StarBody {}---\n'.format(self.name)
        str4=PT.PrettyTable()
        str4.field_names=['Properties','Value']
        str4.add_rows([['1st order velocity(m/s)',self.ad_prop['V1']],
                        ['2nd order velocity(m/s)',self.ad_prop['V2']],
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
        str7='---More are available because of your exploration! And all properties meet SI standard---\n'
        
        return str7
    def __DMegEnergy_Loss(self,T_now=200):
        '''
        ## Get the derivation of the total energy of starbody at specified time, due to megnatic field
        '''
        Meg_t=np.dot(np.array([1,1,0]),self.MegDio)
        return -(BC.mu0*Meg_t**2*self.spin[3]**4)/(6*math.pi*BC.c**3)
    def __MegSpin(self,T_now=100):
        '''
        ## Get the Spin velocity in rad at time T_now, evolve with Megnatic field
        '''
        spin=np.sqrt(1/(T_now*(BC.mu0*self.Radius**6*np.dot(np.array([1,1,0]),self.MegSur)**2)/(3*math.pi*BC.c**3*self.RotI[2])+1/self.spin[2]**2))
        spin=np.array([0,0,spin])
        return spin
    def GWSpin(self,T_now=100):
        '''
        ## Get the Spin velocity in rad at time T_now, evolve with Gravitational Wave field
        '''
        spin=T_now*6*N*BC.G*self.RotI[2]/BC.c**5+1/self.spin[2]**6
        spin=math.pow(1/spin,1/6)
        spin=np.array([0,0,spin])
        return spin
    def __DMegSpin(self,T_now=100):
        return -self.MegSpin(T_now=T_now)[2]**3*(BC.mu0*self.Radius**6*np.dot(np.array([1,1,0]),self.MegSur)**2)/(6*math.pi*BC.c**3*self.RotI[2])
    def __DGWSpin(self,T_now):
        return -N*BC.G*self.RotI[2]/BC.c**5*self.GWSpin(T_now=T_now)[2]**5
    def __DGWEnergy_Loss(self,T_now=200):
        '''
        ## Get the derivation of the total energy of starbody at specified time, due to Gravitational Wave field
        '''
        return -N*BC.G*(self.RotI[0]-self.RotI[1])**2*self.GWSpin(T_now=T_now)**6/BC.c**5
    def __OverAllAmpGW(self,T_now=100,Obser_R=[1e3,1e3,1e3]):
        return 16*math.pi*BC.G*np.abs(self.RotI[0]-self.RotI[1])*(self.GWSpin(T_now=T_now)/(2*math.pi))**2/(BC.c**4*BMech.Vec_Length(Obser_R))

    def Detect_Signal(self,Obser_R=[1e3,1e3,1e3],T_now=200):
        '''
        ## Get the interferometer strain signal of LIGO\n
        ### Parameters:
        - Obser_R: the position vector of the observer
        - T_now: the time at the place of observation
        
        ### Return:
            The Detected Polarized Gravitational Wave Field, [h+,hx]
        '''
        i=BMech.Vec_Angle(Obser_R,self.spin)
        w=self.GWSpin(T_now=T_now)[2]
        w0=self.spin[2]
        h_plus=(-2/BMech.Vec_Length(Obser_R))*(1+np.cos(np.deg2rad(i))**2)*(self.RotI[1]-self.RotI[0])*(w-w0)**2*np.cos(2*(w-w0)*T_now)
        h_cross=(-4/BMech.Vec_Length(Obser_R))*np.cos(np.deg2rad(i))*(self.RotI[1]-self.RotI[0])*(w-w0)**2*np.sin(2*(w-w0)*T_now)
        return [h_plus,h_cross]
    def DATA(self,Dt=10,T_init=0,T_end=1e5,Obser_R=[1e3,1e3,1e3],imgoutput='',Plot=True):
        '''
        ## Plot data of Gravitational wave
        ### Parameters:
        - Dt: the time interval between nearby points
        - T_init: the start time of data
        - T_end: the end time of data
        - Obser_R: the position vector of the observer
        '''
        # Prepare the data
        spin=[]
        signal=[]
        if T_init>=T_end:
            print('Start time {}s is larger than End time {}s!'.format(T_init,T_end))
            return 0

        # Calculate
        time=range(1+int((T_end-T_init)/Dt))
        bar=tqdm(time,mininterval=1)
        bar.set_description('Calculating Gravitational Wave Data')
        for i in bar:
            spin.append(self.GWSpin(T_now=T_init+i*Dt)[2])
            signal.append(self.Detect_Signal(Obser_R=Obser_R,T_now=T_init+i*Dt))

        time=np.array(time)
        time=time*Dt+T_init
        spin=np.array(spin)
        signal=np.array(signal)
        
        # Plot data
        plt.figure(figsize=(16,4))
        plt.subplot(121)
        plt.plot(spin)
        plt.title('Spin Velocity of Pulsar')
        plt.xlabel('Time/s')
        plt.ylabel('rad/s')
        
        plt.subplot(122)
        plt.plot(signal)
        plt.title('Strength of the Polarized Signal h+/hx')
        plt.xlabel('Time/s')
        plt.ylabel('Signal Strength')
        
        # save the data fig
        if imgoutput!='':
            try:
                os.makedirs(imgoutput)
            except:
                pass
            path=os.path.join(imgoutput,'{}_Ti_{}_Te_{}_Dt_{}_Obser_{}.jpg'.format(self.name,T_init,T_end,Dt,Obser_R))
            plt.savefig(path)
            print('---Data image saved as {}---'.format(path))
        # Show the image
        if Plot==True:
            plt.show()# DONOT put plt.show() in front of plt.savefig!!!
        return spin,signal
    

def Reduce_mass(m1,m2):
    return m1*m2/(m1+m2)

def Total_E(m1,m2,Distance):
    return -BC.G*m1*m2/(2*Distance)

def Orbit_spin(m1,m2,Distance):
    return BC.G*(m1+m2)/Distance**3

def Schwarz_Radius(m):
    return 2*BC.G*m/BC.c**2

