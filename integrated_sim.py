class Radioactivity(object):
    def foo(self): 
        pass

class Diffusion(object): 
    def longitudinal(self):
        pass
    def transverse(self):
        pass

class ElectronicNoise(object):
    def electronics(self):
        pass

class Lifetime(object):
    """
    Very small class that applies the electron lifetime effects.
    """
    
    def lifetime(self):
        self.event_data[i,3] = self.electron_lifetime(self.event_data[i,3], drift_times[i])
        
class Simulation(Radioactivity, Diffusion, ElectronicNoise, Lifetime):
    """
    Main class which runs the simulation. Called by GUI for each event and uses the settings to determine which simulation 
    steps are required. 
    """
    
    def __init__(self, settings, event, distance, transDiff, longDiff, seed, IE, velocity, lifetime, electronic_noise):
        """
        Function loads GEANT4 electron data and proceeds through simulation. INPUTS: 
        
        settings        : dictionary of boolean flags containing instructions for which sim steps to compute
        event           : integer event ID matched to GEANT4 event ID tag to extract information from data 
        distance        : the distance of the anode plane from the event origin 
        transDiff       : transverse diffusion coefficient 
        longDiff        : longitudinal diffusion coefficient    
        seed            : np random seed passed from GUI for reproducability 
        IE              : Ionisation energy of argon 
        velocity        : average electron velocity in liquid argon 
        lifetime        : electron lifetime in liquid argon 
        electronic_noise: standard deviation in ADC counts of gaussian kernal 
        """ 
        
        # define simulation variables 
        self.ie          = IE                     # IE of argon in MeV 
        self.v           = velocity               # electron velocity in mm per micro second 
        self.screen      = distance               # position of APA in mm relative to maximum edep position, relative to event origin in x-direction    
        self.lifetime    = lifetime               # electron lifetime in micro seconds 
        self.noise       = electronic_noise       # standard deviation of gaussian used to simulate thermal noise in electronics 
        self.event_num   = event                  # the event ID number used to identify specific neutrino event simulated (from GEANT4) 
        self.t_coef      = transDiff              # transverse diffusion coefficient 
        self.d_coef      = longDiff               # longitudinal diffusion coefficient                        
        np.random.seed(seed)                      # may specify numpy random seed for reproducibility 
        
        # load the data 
        self.electron_data    = np.load('electron_data.npy')

        # extract relevent data for specific event 
        event_idx        = np.where(electron_data[:,5] == event)
        event_idx        = event_idx[0]

        # create empty array to store [x,y,z,edep] of event  
        self.event_data  = np.zeros((len(event_idx), 4), dtype = np.float32)

        # create array to store drift times calculated for each edep in event 
        drift_times = np.zeros((len(event_idx)))
        bunch_screen_intercept = np.zeros((len(event_idx)))

        # create array to hold the locations of each electron in edep bunch after diffusion effects are accounted for 
        event_diffused_locs = np.zeros((1,2))

        # MAINLOOP
        for i in range(len(event_idx)):
            # populate with the correct event data 
            self.event_data[i,0] = electron_data[event_idx[i],0] 
            self.event_data[i,1] = electron_data[event_idx[i],1] 
            self.event_data[i,2] = electron_data[event_idx[i],2] 
            self.event_data[i,3] = electron_data[event_idx[i],3] / self.ie

            # work out each bunch-screen intercept and drift distance 
            distance_travelled          = abs(self.screen - self.event_data[i,0])
            drift_times[i]              = distance_travelled / self.v
            intercept                   = self.calc_intercept(self.event_data[i,:3]) 
            bunch_screen_intercept[i]   = intercept[1]

            # check if electron lifetime flag is TRUE 
            if settings["lifetime"] == True: 
                self.lifetime()
            






