import PurpleMicroStar.StarBody as SB
import PurpleMicroStar.MultiBody as MB
import PurpleMicroStar.BasicMech as BMech
import PurpleMicroStar.BasicConst as BC
import PurpleMicroStar.GravitationalWave as GW
import PurpleMicroStar

import click
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle


@click.command()
@click.option('--dt',default=100,help='The time per iteraration suffers, in s')
@click.option('--iter',default=1e5,help='The total iteration times')
@click.option('--output',default='C:\\MultiBody-CurveData',help='The output folder')
def PMS(dt,iter,output):
    sb1=SB.StarBody()
    print(sb1)
    mb1=MB.MultiBody()
    # print(PurpleMicroStar.__path__)
    mb1.Dataset(datapath=os.path.join(PurpleMicroStar.__path__[0],'exampledata\\Multibody-3.csv'))
    print(mb1)
    bh1=GW.CBIGW()
    print(bh1)
    bh2=GW.CGW()
    print(bh2)

    bh2.DATA()
    mb1.Iteration(dt=dt,iterCount=iter,output=output)
    mb1.Plot()
    

# def StarBody()



if __name__=='__main__':
    PMS()
