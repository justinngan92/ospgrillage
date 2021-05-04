# Overview

The `ops-grillage` module is a python wrapper for ```Openseespy``` module. ```Openseespy``` 
is a Python interpreter of Open System for Earthquake Engineering Simulation (OpenSees) software framework.
`ops-grillage` allow python users to create py file that generates a grillage model in Openseespy.

A typical output py file from the wizard contains relevant ```Openseespy``` commands for constructing a 
model in Opensees domain. The commands are automatically generated based on user specified inputs 
regarding the bridge model. The wrapper allows quick generation of py file with few basic command lines in Python 
interface. This module lowers the bar for research, education, and training of the software for structural
analysis purposes.

## Installation

To run the wrapper, download from github link() and import the following files:
    
    import OpsGrillage as og
    
For detailed information on installation, refer to [installation]


## Documentation

See :ref:Structure description page for more information of inputs. 

## Current Capabilities

### Bridge model feature
- [x] Skew meshing
- [x] Orthogonal meshing
- [x] Positive and negative skew angle
- [x] Allowance for skew mesh to be set up to 30 degrees
- [x] Allowance for orthogonal mesh to be set down to 11 degrees
- [x] Grillage elements grouped allowing definition of element group properties with single line function 
- [x] Autodetect edge of spans as supporting nodes
- [x] Automatically set transverse slab properties to slab elements based on input unit width properties


### Model utility feature
- [x] Gravity Load analysis check
- [x] Test/check output file functionality
- [x] Alternative plotting feature available as an extension of the default Opensees plotting module


### In the works
- [ ] Grouping feature for skew mesh - accommodate for customized nodes 
- [ ] Allow representation of diaphragm in model
- [ ] Allow representation of transverse secondary beams in model
- [ ] Enable multi-span definition 
- [ ] Capable to shift origin of mesh generation
- [ ] Combine individual mesh generation to a single mesh 
- [ ] Allow customized nodes for meshes
