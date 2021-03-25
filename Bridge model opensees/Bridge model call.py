from Bridgemodel import *
from Bridge_member import BridgeMember
import pandas as pd
import matplotlib.pyplot as plt
# ---------------------------------------------------------------------------------------------------------------------
# Opensees model generation for Bridge class
# ---------------------------------------------------------------------------------------------------------------------

# Model inputs


# CONCRETE      f'c    ec0    f'cu   ecu
concreteprop = [-6.0, -0.004, -6.0, -0.014]
steelprop = []
# # define bridge element properties
#                           A  E  G  Jx  Iy   Iz                   # N m
#longbeam = BridgeMember(0.41631,31.113E9 ,1 ,4.23662E-3,0.0380607,0.0484717)
#LRbeam = BridgeMember(0.543153,31.113E9 ,1 ,9.41034E-3 ,0.0634485 ,0.0646434)
#edgebeam = BridgeMember(7.5E-3,31.113E9 ,1 ,4.93885E-6 ,1.5625E-6 ,14.0625E-6)
#slab = BridgeMember(0.116129,31.113E9 ,1 ,0.392896E-3 ,5.61912E-3,0.224765E-3)
#diaphragm = BridgeMember(0.0580644,31.113E9 ,1 ,0.168245E-3 ,0.702391E-3 ,0.112382E-3)

# = = =  = = = =  = = =  = = = = = = = = =  = = = =  = = =  = = = = = = = = =  = = = =  = = =  = = = = = = =
beamelement = "ElasticTimoshenkoBeam"
#beamelement = "elasticBeamColumn"
#                           A  E  G  Jx  Iy   Iz     Avy  Avz       # N m
#longbeam = BridgeMember(0.896,34.6522E9 ,20E9 ,0.133,0.214,0.259,0.233,0.58,beamelement)
#LRbeam = longbeam
#edgebeam = BridgeMember(0.044625,34.6522E9 ,20E9 ,0.26E-3 ,0.114E-3,0.242E-3,0.0371875,0.0371875,beamelement)
#slab = BridgeMember(0.4428,34.6522E9 ,20E9 ,2.28E-3 ,0.2233,1.19556E-3,0.369,0.369,beamelement)
#diaphragm = BridgeMember(0.2214,34.6522E9,20E9 ,2.17E-3 ,0.111,0.597E-3,0.1845,0.1845,beamelement)

Nodedetail = pd.read_excel('Benchmark bridge.xlsx',sheet_name = 'Node')
Connectivitydetail = pd.read_excel('Benchmark bridge.xlsx',sheet_name = 'Connectivity')
Memberdetail = pd.read_excel('Benchmark bridge.xlsx',sheet_name = 'Member')

# = = =  = = = =  = = =  = = = = = = = = =  = = = =  = = =  = = = = = = = = =  = = = =  = = =  = = = = = = =
#  Inputs: Lz,  skew angle, Zspacing, number of beams, Lx, Xspacing,:
#Bridge2 = OpenseesModel(10.175, 0, 2, 5, 24.6, 2.46,beamelement)

Bridge2 = OpenseesModel(Nodedetail,Connectivitydetail,beamelement,Memberdetail)

#  Inputs: Lz,  skew angle, Zspacing, number of beams, Lx, Xspacing,:
#Bridge2 = Bridgemodel.OpenseesModel(10.11, 0, 1.4224 , 7, 18.288, 0.762)
#Bridge2.assign_beam_member_prop(longbeam.get_beam_prop,LRbeam.get_beam_prop,edgebeam.get_beam_prop,slab.get_beam_prop, diaphragm.get_beam_prop)
Bridge2.assign_material_prop(concreteprop,steelprop)
# Notes
# ---------------------------------------------------------------------------------------------------------------------
# Model generation
Bridge2.create_Opensees_model()
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

# Moving load analysis - Combinations of truck position
Bridge2.time_series()
Bridge2.loadpattern()
#                           x y z mx my mz (N m)
#  eg.load_singlepoint(50,[100000,-50000,-50000,0,0,0])

# Truck definition
axlwts = [800, 3200, 3200]  # N  # length of axlwts dictates how many axles (e.g. a 5 axle truck will have len = 5)
axlspc = [16.8, 16.8]  # m   # len of axlspc should correspond to len(axlwts) - 1 , since its the spacing
axlwidth = 5  # m    # width of truck

# Enter: "First point",
Xloc = [0]      # initial load location (front tyre heading from X = 0)
Zloc = 0        # top axle with resp to Z axis, starting from Z = 0. (code auto calcs bott axle based on truck width)

Bridge2.load_position([0,4],-1000)
#Bridge2.loadID()
#Bridge2.load_movingtruck([13.5,5],axlwts,axlspc,axlwidth)

# ------------------------------
# Start of analysis generation
# ------------------------------

#wipe analysis
wipeAnalysis()

# create SOE
system("BandSPD")

# create DOF number
numberer("RCM")

# create constraint handler
constraints("Plain")

# create integrator
integrator("LoadControl", 1.0)

# create algorithm
algorithm("Linear")

# create analysis object
analysis("Static")

# perform the analysis
analyze(1)

# Print node displacement results at midspan
#print(nodeDisp(6))              # OpenseesModel's method accessible from outside of OpenseesModel class.
#print(nodeDisp(17))
#print(nodeDisp(28))
#print(nodeDisp(39, 0))
#print(nodeDisp(50, 0))
#print(nodeDisp(61, 0))
#print(nodeDisp(72, 0))

print([nodeDisp(1)[1],nodeDisp(2)[1],nodeDisp(3)[1],nodeDisp(4)[1],nodeDisp(5)[1],nodeDisp(6)[1],
      nodeDisp(7)[1],nodeDisp(8)[1],nodeDisp(9)[1],nodeDisp(10)[1],nodeDisp(11)[1]])
#plt.plot([nodeDisp(1)[1],nodeDisp(2)[1],nodeDisp(3)[1],nodeDisp(4)[1],nodeDisp(5)[1],nodeDisp(6)[1],
      #nodeDisp(7)[1],nodeDisp(8)[1],nodeDisp(9)[1],nodeDisp(10)[1],nodeDisp(11)[1]])


#plt.plot([eleForce(1+t)[n],eleForce(2+t)[n],eleForce(3+t)[n],eleForce(4+t)[n],eleForce(5+t)[n],eleForce(6+t)[n],
  #    eleForce(7+t)[n],eleForce(8+t)[n],eleForce(9+t)[n],eleForce(10+t)[n]])

#plt.plot([eleForce(1+u)[n],eleForce(2+u)[n],eleForce(3+u)[n],eleForce(4+u)[n],eleForce(5+u)[n],eleForce(6+u)[n]])

#plt.show()
print('load at 10 8')
breakpoint()
#Bridge2 = OpenseesModel(Nodedetail,Connectivitydetail,beamelement,Memberdetail)


# first analysis + second point load
Bridge2.load_position([1,4],-1000)
#wipe analysis
#wipeAnalysis()



# perform the analysis
analyze(1)

print([nodeDisp(1)[1],nodeDisp(2)[1],nodeDisp(3)[1],nodeDisp(4)[1],nodeDisp(5)[1],nodeDisp(6)[1],
      nodeDisp(7)[1],nodeDisp(8)[1],nodeDisp(9)[1],nodeDisp(10)[1],nodeDisp(11)[1]])
print('wipe analysis- then load at 1 4')
breakpoint()
print("Operation finished")