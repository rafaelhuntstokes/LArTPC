import numpy as np 
import matplotlib.pyplot as plt 
import mpl_toolkits.mplot3d.axes3d as axes3d
from time import time
from math import exp, pi, cos, sin
from scipy.stats import binned_statistic_2d as hist 
from scipy.stats import multivariate_normal as gauss2D
from scipy.stats import norm
from scipy.stats import poisson
from scipy.stats import rv_continuous
from scipy.interpolate import interp1d as transform
import scipy.integrate as integrate
from skimage.filters import gaussian
import os


class beta_smearing(object):
    """
    This class handles the smearing of radioactive beta particles, improving on the point-deposition approximation. 
    Each decay creates an electron with energy sampled from beta decay spectrum. This energy is used to determine its 
    distance of travel based on a fit to a Moyal/Landau sample made elsewhere. The energy of the electron is deposited 
    in descrete, equally sized packets along its trajectory.
    """

    def smear_master(self, decay_data, num_decays):

        NUM_DECAYS = int(num_decays) # the number of radioactive decays within event volume 
        STEP_SIZE  = 0.5             # the step size, used to discretise the range of the beta particle 

        # find distance travelled by each beta particle 
        decay_data[:,5] = self.distance(decay_data[:,4])
        
        # find the final location based on a random direction vector of beta particle 
        f_locs = np.zeros((NUM_DECAYS, 3), dtype=np.float32)
        f = self.random_vector(decay_data[:,5], decay_data[:,0:3])
        f_locs[:,0] = f[0]
        f_locs[:,1] = f[1]
        f_locs[:,2] = f[2]
        
        # divide the distance travelled into discrete steps and find number of drift electrons produced at each step 
        chunked = self.chunking(decay_data[:,5], STEP_SIZE, decay_data[:,4])
        number_deps = sum(chunked[:,1])
        
        # |X|Y|Z|Tpos|num|
        output_data = np.zeros((int(number_deps), 5), dtype=np.float32)
        curr_idx = 0 
        for i in range(NUM_DECAYS):
            # find direction vector of size equal to step size from initial and final location 
            vec = np.array((f_locs[i,0], f_locs[i,1], f_locs[i,2])) - np.array((decay_data[i,0], decay_data[i,1], decay_data[i,2]))
            normed = np.linalg.norm(vec)
            vec = (vec /normed) * STEP_SIZE
            
            # apply vector for required number of times to position to get each edep location 
            for j in range(int(chunked[i,1])):
                output_data[curr_idx, 0] = decay_data[i,0] + vec[0]*j
                output_data[curr_idx, 1] = decay_data[i,1] + vec[1]*j
                output_data[curr_idx, 2] = decay_data[i,2] + vec[2]*j
                output_data[curr_idx, 3] = decay_data[i,3] 
                output_data[curr_idx, 4] = chunked[i,2]
                curr_idx += 1 
        
        return output_data

    def plot(self, init_data, f_locs, f_data):
        """
        Plots the decays, edeps and trajectories all on 1 massive 3D graph. This function is not used by default and should only be used to 
        create plots for demonstration/sanity checking purposes. 
        """

        # create the figure 
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1, projection = '3d')

        # plot initial decay locations 
        ax.scatter(init_data[:,0], init_data[:,1], init_data[:,2], color = 'k')

        # plot final decay locations 
        ax.scatter(f_locs[:,0], f_locs[:,1], f_locs[:,2], color = 'r') 

        # plot scatter each edep position 
        p = ax.scatter(f_data[:,0], f_data[:,1], f_data[:,2], c=f_data[:,4], cmap = 'inferno')
        fig.colorbar(p)

        # plot the trajectory from initial point to final point 
        for i in range(len(init_data[:,1])):
            ax.plot((init_data[i,0],f_locs[i,0]), (init_data[i,1], f_locs[i,1]), (init_data[i,2], f_locs[i,2]), color = 'k', linestyle = '--', linewidth = 0.5)

        plt.title("Beta Decay Energy Deposition Locations")
        plt.xlabel('x / mm')
        plt.ylabel('y / mm')
        ax.set_zlabel('z / mm')
        plt.show()

    def distance(self, energy):
        """
        Function calculates the distance travelled for a given initial energy from a y = mx + c fit to av. Moyal fluctuation plot (found in chapter 2 of report).
        """

        return (0.685*energy + 0.156)*10 # x10 to go from cm --> mm 

    def random_vector(self, distance, init_data):
        """
        Create a random final location on surface of sphere, radius = distance travelled, centered on initial decay location. This method is not perfect - 'uniform' distribution 
        is actually clustered around the poles of sphere. Need to upgrade to take into account integrals/surface elements etc...But it is good enough for now! 
        """

        # spherical coordinates
        theta = np.random.uniform(low = 0, high = pi, size = len(distance))
        phi   = np.random.uniform(low = 0, high = 2*pi, size = len(distance))

        # find x y z location 
        x = distance * np.sin(theta) * np.cos(phi)
        y = distance * np.sin(theta) * np.sin(phi)
        z = distance * np.cos(theta)

        f_loc = (init_data[:,0]-x,init_data[:,1]-y,init_data[:,2]-z)

        return f_loc 

    def chunking(self, distance, step_size, energy):
        """
        Function divides up trajectory and finds energy deposition and number of drift electrons created at each step.
        """

        unit_distance = distance // step_size
        #print(unit_distance)
        # divide energy deposited along each step and convert to drift electrons 
        edep = energy / unit_distance 
        drift = edep / 23.6e-6
        smeared_data = np.zeros((len(distance), 3), dtype = np.float32)
        smeared_data[:,0] = distance
        smeared_data[:,1] = unit_distance
        smeared_data[:,2] = drift 
        #print('deposit data:', smeared_data)
        return smeared_data

class radiation_package(beta_smearing):
    """
    This class contains the methods required to simulate the radiological background noise recorded during the event. Inherits beta_smearing class methods to 
    more accuractely model emitted beta particle contributions. 
    """

    def event_volume_rate(self, drift_times):
        """
        Take event data (populated), draw a volume cube around it and work out mean rate.
        """

        # find max dims of event 
        x_volume = max(self.event_data[:,0]) - min(self.event_data[:,0])
        y_volume = max(self.event_data[:,1]) - min(self.event_data[:,1])
        z_volume = max(self.event_data[:,2]) - min(self.event_data[:,2])

        vol           = 2 * x_volume * y_volume * z_volume  # double the volume of the event (arbitrary)
        vol_module    = 7e12                                # volume of single phase module in mm^3
        rateAr_module = 10                                  # rate of decay in a module per micro second for Ar-39  
        rateK_module  = 1e-3                                # rate of decay in a module per micro second for K-31 
        t_max         = max(drift_times)                    # amount of time spanned by the event in micro seconds 
        
        # based on mean rate of Ar-39 find mean in that volume 
        # within -500 to +500 micro seconds ... 
        rateAr = rateAr_module * vol/vol_module * 1000
        rateK = rateK_module * vol/vol_module * 1000
        
        # pass the mean rates to events_observed function 
        return self.events_observed(rateAr, rateK, t_max) 

    def events_observed(self, rateAr, rateK, t_max):
        """
        Given a mean rate, returns the number of observed events from a Poisson distribution.
        """

        obs_eventsAr = poisson(rateAr).rvs(size = 1)
        obs_eventsK = poisson(rateK).rvs(size = 1)
        print('observed Ar: {}\nobserved K: {}'.format(obs_eventsAr, obs_eventsK))

        # pass the number of decays observed to populate_radio_data function 
        return self.populate_radio_data(obs_eventsAr, obs_eventsK, t_max)
    
    def bd_Ar(self, x):
        """
        Unnormalised pdf for Argon beta spectrum. Function is found from Fermi theory ignoring fermi function correction. 
        """
        return (np.sqrt(x**2 + 2*x*0.511)*((0.6-x)**2)*(x+0.511)) 

    def bd_K(self, x):
        """
        Unnormalised pdf for potassium spectrum. Function is found from Fermi theory ignoring fermi function correction.
        """
        return (np.sqrt(x**2 + 2*x*0.511)*((3.5-x)**2)*(x+0.511)) 
    
    def beta_spect(self, q_value, num_events):
        """
        Function creates and samples beta decay energy spectrum.
        """
        # define bounds 
        a = 0 
        b = q_value

        # find normalised pdf 
        if q_value == 3.5:
            pdf = self.bd_K
        else:
            pdf = self.bd_Ar
        norm = integrate.quad(pdf, a, b)
        
        # create custom beta decay spectrum
        class beta_decay(rv_continuous, radiation_package):
            def _pdf(self, x):
                if q_value == 3.5:
                    return self.bd_K(x)/norm[0]
                else: 
                    return self.bd_Ar(x)/norm[0]

        # sample distribution 
        decay = beta_decay(a =a, b = b)
        rand = decay.rvs(size = num_events)

        return rand

    def ionisation_distance(self, energy):
        """
        Function uses fit to Moyal distance plot to find expected distance travelled by beta particle.
        """

        return (0.685*energy + 0.156)*10 # eqn from fit and x10 to get cm -> mm 
        
    def  populate_radio_data(self, obs_eventsAr, obs_eventsK, t_max):
        """
        Function takes the number of observed events and populates an array with the 
        emitted beta particle information: [x,y,z,E].
        """

        # create empty array to hold beta decay particle data 
        total_events = obs_eventsK + obs_eventsAr
        radiodata = np.zeros((int(total_events),6), dtype=np.float32) 

        # define the Q-values for each decay type - used to generate beta decay spectrums
        q_Ar = 0.6 # MeV
        q_K  = 3.5 # MeV 
        
        # sample from uniform distributions within the event volume cube to find x,y,z,t position of each decay 
        x_vals = np.random.uniform(min(self.event_data[:,0]),max(self.event_data[:,0]), size = total_events)
        y_vals = np.random.uniform(min(self.event_data[:,1]),max(self.event_data[:,1]), size = total_events)
        z_vals = np.random.uniform(min(self.event_data[:,2]),max(self.event_data[:,2]), size = total_events)
        t_vals = np.random.uniform(-500, 500, size = total_events)
        
        # sample beta decay spectrum to get the energy of each emitted beta particle  
        # calls beta_spect method defined above 
        e_spectAr = self.beta_spect(q_Ar, obs_eventsAr)
        e_spectK  = self.beta_spect(q_K, obs_eventsK) 

        # populate radiodata with decay information
        j = 0 
        for i in range(int(total_events)):
            radiodata[i,0] = x_vals[i]
            radiodata[i,1] = y_vals[i]
            radiodata[i,2] = z_vals[i]
            radiodata[i,3] = t_vals[i]
            try:
                radiodata[i,4] = abs(e_spectAr[i]) #/ 23.6e-6
            except: 
                radiodata[i,4] = abs(e_spectK[j]) #/ 23.6e-6
                j +=1
        
        if self.SMEAR == True:
            # pass to the smearing class functions to get edep along the trajectory 
            radiodata = self.smear_master(radiodata, total_events)
        else:
            radiodata[:,4] = radiodata[:,4] / 23.6e-6
        return radiodata 

class simulation(radiation_package):
    """
    Main class object which runs the simulation. Inherits methods from the radiation package class defined above to deal with radiological noise. 
    Takes defaults and GEANT4 neutrino event data as inputs and returns TPC image of event. Changeable physics parameters include: 
    electron lifetime; APA distance relative to event; electron velocity (and by extension uniform E field strength); longitudinal and transverse diffusion coefficents; thermal noise std; 
    radiological activity.
    """

    def __init__(self, event, screen,lifetime, t_coef, d_coef):
        
        # load the neutrino event data produced by GEANT4 
        electron_data    = np.load('electron_data.npy')

        # extract relevent data for specific event 
        event_idx        = np.where(electron_data[:,5] == event)
        event_idx        = event_idx[0]

        # create empty array to store [x,y,z,edep] of event  
        self.event_data  = np.zeros((len(event_idx), 4), dtype = np.float32) 

        # define simulation defaults/physics variables 
        self.ie          = 23.6e-6                     # IE of argon in MeV 
        self.v           = 1.6                         # electron velocity in mm per micro second 
        self.screen      = screen                      # position of APA in mm relative to maximum edep position, relative to event origin in x-direction    
        self.lifetime    = lifetime                    # electron lifetime in micro seconds 
        self.noise       = 5                           # standard deviation of gaussian used to simulate thermal noise in electronics 
        self.event_num   = event                       # the event ID number used to identify specific neutrino event simulated (from GEANT4) 
        self.t_coef      = t_coef                      # transverse diffusion coefficient 
        self.d_coef      = d_coef                      # longitudinal diffusion coefficient                        
        np.random.seed(3)                              # may specify numpy random seed for reproducibility 
        self.ACTIVE = True                             # if TRUE, simulate radiological noise 
        self.SMEAR = True                              # if TRUE, do not assume point deposition of beta decay energy - more accurate, but more time consuming 
        
        # create array to store drift times calculated for each edep in event 
        drift_times = np.zeros((len(event_idx)))
        bunch_screen_intercept = np.zeros((len(event_idx)))

        # create array to hold the locations of each electron in edep bunch after diffusion effects are accounted for 
        event_diffused_locs = np.zeros((1,2))
        
        # MAINLOOP
        for i in range(len(event_idx)):
            self.event_data[i,0] = electron_data[event_idx[i],0] 
            self.event_data[i,1] = electron_data[event_idx[i],1] 
            self.event_data[i,2] = electron_data[event_idx[i],2] 
            self.event_data[i,3] = electron_data[event_idx[i],3] / self.ie

            # work out each bunch-screen intercept and drift distance 
            distance_travelled          = abs(self.screen - self.event_data[i,0])
            drift_times[i]              = distance_travelled / self.v
            intercept                   = self.calc_intercept(self.event_data[i,:3]) 
            bunch_screen_intercept[i]   = intercept[1]
            
            # apply electron lifetime 
            self.event_data[i,3] = self.electron_lifetime(self.event_data[i,3], drift_times[i])

            # diffusion effects 
            std_time, std_space       = self.diffusion_calcs(drift_times[i], distance_travelled)
            cov                       = [[std_time**2,0], [0, std_space**2]]
            self.mean                 = [drift_times[i], bunch_screen_intercept[i]]
            bunch_diffused_locations  = np.random.multivariate_normal(mean = self.mean, cov = cov, size = int(self.event_data[i,3]))
            event_diffused_locs       = np.concatenate((event_diffused_locs, bunch_diffused_locations))

        if self.ACTIVE==True: 

            # add in the radioactive noise clusters 
            radiodata = self.event_volume_rate(drift_times)
            radio_drift = np.zeros((len(radiodata[:,0])), dtype = np.float32)
            bunch_screen_intercept = np.zeros((len(radiodata[:,1])))

            for i in range(len(radio_drift)):

                # populate drift times and find intercept points 
                distance_travelled          = abs(self.screen - radiodata[i,0])
                radio_drift[i]              = distance_travelled / self.v
                intercept                   = self.calc_intercept(radiodata[i,:3]) 
                bunch_screen_intercept[i]   = intercept[1]

                # electron lifetime 
                radiodata[i,4] = self.electron_lifetime(radiodata[i,4], radio_drift[i])
                
                # diffusion effects 
                std_time, std_space       = self.diffusion_calcs(radio_drift[i], distance_travelled)
                cov                       = [[std_time**2,0], [0, std_space**2]]
                self.mean                 = [radio_drift[i], bunch_screen_intercept[i]]
                bunch_diffused_locations  = np.random.multivariate_normal(mean = self.mean, cov = cov, size = int(radiodata[i,4]))

                # add time of creation to drift time to get time hitting screen 
                bunch_diffused_locations[:,0] += radiodata[i,3] 
                event_diffused_locs       = np.concatenate((event_diffused_locs, bunch_diffused_locations))

        # transform all the data points to +ve space for binning 
        event_diffused_locs[:,1] = self.positive_transform(event_diffused_locs[:,1])
        min_pos = min(event_diffused_locs[:,1])
        max_pos = max(event_diffused_locs[:,1])

        # normalise each position from 0->1 
        space_range  = [min_pos, max_pos]
        space_normed = [0, 1]
        space_transform = transform(space_range, space_normed)
        event_diffused_locs[:,1] = space_transform(event_diffused_locs[:,1])

        # bin all the data according to the dimensions of the detector
        t_max = np.amax(event_diffused_locs[:,0])
        Xedge = np.arange(0, 1, 1/960)
        Yedge = np.arange(-500, 500, 2)

        # create TPC image (histogram with number of hits on each wire for each 2 micro second time interval)
        signal = hist(event_diffused_locs[:,0], event_diffused_locs[:,1], bins = [Yedge, Xedge], statistic = 'count', values = event_diffused_locs[:,0])[0]
        shape = signal.shape
       
        # convert to ADC counts 
        adc_range = [500,4091]

        # arbitrary max hits, anything above will  be max ADC (saturation)
        hits_range = [0, 4500] 
        ADC = transform(hits_range, adc_range, bounds_error = False, fill_value = 4091)
        flat_sig = signal.flatten()
        signal = ADC(flat_sig)
        signal = signal.reshape((shape))

        # add gaussian smears in time due to electronic noise
        signal = self.gaussian_blur(signal)
        signal = self.gaussian_noise(signal)
        self.result = signal
        
        #plot or save the TPC image 
        self.plot_image(signal)

    def plot_image(self, image):

        #plt.figure()
        #ax = fig.set_ylim(bottom = -500)
        #plt.xlabel('Wire Number')
        #plt.ylabel('Time (2 micro s)')
        #if self.ACTIVE == True: 
            #plt.title('Event {} {}'.format(self.event_num, 'Event 0 with Radioactive Decay Smearing'))
        #if self.ACTIVE == False: 
            #plt.title('Event {} with Diffusion & Noise'.format(self.event_num))
        #plt.imshow(image, vmin = 495, vmax = 4091)
        #plt.show()

        # save the TPC image in the directory specified 
        dir = 'lifetime_test{}'.format(self.lifetime)
        try:
            os.mkdir(dir)
        except:
            pass
        plt.imsave('./'+dir+'/sn_{}.jpeg'.format(self.event_num),image, vmin = 450, vmax = 4091)

    def plot_distributions(self, image):
        """
        Function no longer used, but potential can create a trace of the signal on each wire.
        """

        wire_nums = np.arange(959)
        total_sig1 = []
        total_sig2 = []
        for i in range(959):
            val1 = np.amax(image[:,i])
            total_sig1.append(val1)

        plt.figure()
        plt.bar(wire_nums, total_sig1)
        plt.title('Peak Wire Signals - mean{}'.format(self.mean))
        plt.xlabel('Wire Number')
        plt.ylabel('ADC Counts')
        plt.show()

        return total_sig1
        
    def diffusion_calcs(self, drift_time, distance): 
        """
        Function returns the standard deviation of each diffusion direction. 
        """

        # longitudinal diffusion in time 
        t_std = np.sqrt(2*distance*self.t_coef/self.v**3)

        # transverse diffusion in space 
        s_std = 2*np.sqrt(self.d_coef*drift_time)

        return t_std, s_std 
    
    def electron_lifetime(self, bunch_pop, drift_time): 
        """
        Simple attenuation function to model electron attachement to electrongeative impurities in the LAr. Decaying exponential.
        """

        return bunch_pop*exp(-drift_time/self.lifetime)

    def calc_intercept(self, location):
        """
        Intercept between electron bunch and APA. Assumes shortest distance, straight line trajectory.
        """

        # point on the plane: 
        plane_point = np.array((self.screen,1,1))
        
        # normal vector 
        n = np.array((5,0,0))

        # calculate the scale factor, t, in intersept eqn: ro + d * t
        t = (np.dot((plane_point - location), n)/(np.dot(n,n)))
        intercept = location[0:3] + t * n
        
        return intercept
    
    def gaussian_blur(self,image):
        """
        Accounts for imperfect response of electronics in time by smearing TPC image vertically with a std of 2 time bins. 
        """

        return gaussian(image, sigma=(2,0), truncate = 10, multichannel=False)

    def gaussian_noise(self,image):
        """
        Adds thermal electronic noise.
        """

        noise = np.random.normal(loc = 0.0, scale = self.noise, size = image.shape)

        return image + noise 
    
    def positive_transform(self,event_data):
        """
        Transforms all the bunch locations to positive space for easier handling. 
        """

        # find minimum z coordinates 
        z_min = np.amin(event_data)
        
        # check if negative - yes, rescale to zero
        if z_min < 0: 
            for i in range(len(event_data)):
                event_data[i] = event_data[i] - z_min 
                
        return event_data


"""
This code stub calls the above simulation class to create TPC images for the first 2000 GEANT4 events (in electron_data.txt) for different lifetimes.
"""
# lifetimes = [2,4,6,8,10,15,20,25,30,35,40,45,50,60,70,80,90,100,200,300] #micro seconds 
# start = time()
# for i in lifetimes:
#     for j in range(1):
#         x = simulation(j,10,i, 7.4e-4,24e-4)
#         print('COMPLETED EVENT {} for rad {}'.format(j, i))
# end = time()
# print(end-start)