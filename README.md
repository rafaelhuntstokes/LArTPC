# LArTPC
A simulation of DUNE's far detector. This software package was created as part of an MSci research project, under the supervision of Professor Ryan Nichol @ UCL. The simulation takes event data, generated in GEANT4, of CC- supernova neutrino/argon interactions, and uses it to output TPC images. These images are sensative to a variety of the physics parameters of the detector, such as electron lifetime, diffusion coefficients, electron velocity, radioactive activity and electronic noise.

The simulation outputs a set of supernova neutrino event images and images comprised only of noise. A convolutional neural network is used to investigate classification accuracy under a range of different conditions. 

NOTE: the required GEANT4 data for the simulation, electron_data.npy, is too large to upload here. 
