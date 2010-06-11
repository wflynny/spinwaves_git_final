import sys, os
pth = os.path.join(r'C:\tripleaxisproject-local',os.path.join(r' tripleaxisproject','rescalculator'))
sys.path.append(os.path.join(r'C:\\',pth))

import numpy as np
from smabifeo3 import SMADemo
from prefdemo_bifeo3 import PrefDemo

H,K,L = (1,0,0)
p=np.zeros(6)
x = SMADemo(H,K,L,p)
print x