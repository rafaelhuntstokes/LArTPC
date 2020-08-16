import tkinter as tk 
from tkinter import messagebox
import numpy as np 
from PIL import ImageTk,Image

class defaultsGUI(object):
    """
    This class handles the window allowing user to set default values for dependent simulation parameters.
    """
    def setupDefaultWindow(self): 
        
        # setup simulation default values and variables 
        self.SEED             = np.random.randint(0,100) 
        self.DISTANCE         = 3.53   # (m) 
        self.TRANSDIFF        = 7.2e-4 # (m^2 s^-1) 
        self.LONGDIFF         = 12e-4  # (m^2 s^-1)
        self.ELECTRONIC_NOISE = 5      # std in ADC counts 
        self.NUMBER_EVENTS    = 100    # number of events to simualate

        # # delete all the current frame widgets 
        self.lifetimeBtn.destroy()
        self.elecNoiseBtn.destroy()
        self.radioactivityBtn.destroy()
        self.variableQ.destroy()
        self.spaceFrame.destroy()

        # create frames for first panel of default widgets and navigation buttons 
        self.general = tk.LabelFrame(window, text = "General Settings")
        self.navigation = tk.LabelFrame(window, text = "Navigation") 
        self.general.grid(column = 1) 
        self.navigation.grid(column = 2)

        # create widgits
        self.seedWidgit()         # set seed 
        self.anodeWidgit()        # drift distance slider
        self.diffusionCoeffs()    # long and trans diffusion coeffs 
        self.electronics()        # electronic noise kernel STD
        self.events()             # number of events 
        self.navButtons()         # confirm and back buttons 

    def navButtons(self):
        """
        Function creates a confirm button to launch simulation and a back button to return to independent variable selection screen. 
        """

        self.backBtn = tk.Button(self.navigation, text = "Back", command = self.back)
        self.backBtn.grid(row = 0, column = 1, sticky = "nswe")

        self.goBtn = tk.Button(self.navigation, text = "Start", command = self.runSim)
        self.goBtn.grid(row = 0, column = 2, sticky = "nswe")

    def back(self):
        """
        Return to independent variable selection screen. 
        """
        
        # destroy all current widgets in frame
        self.general.destroy()
        self.navigation.destroy()

        # call method to re-create the variable selection window 
        self.createData()


    def runSim(self):
        pass

    def events(self):
        """
        Function allows you to choose the number of events to simulate. 
        """

        self.eventsLabel = tk.Label(self.general, text = "Number of Events")
        self.eventsLabel.grid(row = 5, column = 0)

        number = tk.IntVar()
        number.set(self.NUMBER_EVENTS)

        self.eventSlide = tk.Scale(self.general, variable = number, from_ = 1, to = 10000, orient = "horizontal", length = 200, resolution = 50)
        self.eventSlide.grid(row = 5, column = 1, columnspan = 3)

        
    def electronics(self): 
        """
        Widgit lets you set set standard deviation of gaussian blur for electronic noise response. Checks if electronic noise 
        is the independent variable - if yes, fills in the values previously given. 
        """

        self.elecLabel = tk.Label(self.general, text = "Electronic Noise STD")
        self.elecLabel.grid(row = 4, column = 0)

        elecNoise = tk.DoubleVar()

        if self.parameter != "electronic":
            # electronic noise is a dependent variable to be specified as a constant 
            elecNoise = tk.DoubleVar()
            elecNoise.set(self.ELECTRONIC_NOISE)

            self.elecBtn = tk.Button(self.general, text = "Edit?", command = lambda: self.setState(self.elecEntry))
            self.elecBtn.grid(row = 4, column = 1)
        
        else: 
            # electronic noise is the independent variable, with values already set. Fill widget with these values. 
            self.ELECTRONIC_NOISE = self.parameterSpace
            elecNoise.set(self.ELECTRONIC_NOISE)

            self.elecInfo = tk.Label(self.general, text = "INDIE. VAR")
            self.elecInfo.grid(row = 4, column = 1)

        self.elecEntry = tk.Entry(self.general, textvariable = elecNoise, state = "disabled")
        self.elecEntry.grid(row = 4, column = 2)

    def diffusionCoeffs(self):
        """
        Creates the widgit for displaying/altering the diffusion coefficients.
        """

        transdiff = tk.DoubleVar()
        longdiff  = tk.DoubleVar()

        transdiff.set(self.TRANSDIFF)
        longdiff.set(self.LONGDIFF)

        self.transLabel = tk.Label(self.general, text = "Longitudinal Diffusion Coefficient")
        self.longLabel  = tk.Label(self.general, text = "Transverse Diffusion Coefficient")
        self.transLabel.grid(row = 2, column = 0)
        self.longLabel.grid(row = 3, column = 0)

        self.transEntry = tk.Entry(self.general, textvariable = transdiff, state = "disabled")
        self.longEntry  = tk.Entry(self.general, textvariable = longdiff, state = "disabled")
        self.transEntry.grid(row = 2, column = 2)
        self.longEntry.grid(row = 3, column = 2)

        self.transBtn = tk.Button(self.general, text = "Edit?", command = lambda: self.setState(self.transEntry))
        self.longBtn  = tk.Button(self.general, text = "Edit?", command = lambda: self.setState(self.longEntry))
        self.transBtn.grid(row = 2, column = 1)
        self.longBtn.grid(row = 3, column = 1)


    def setState(self, widgit):
        """
        Allow changing of a widgit state.
        """

        if widgit['state'] == 'normal':
            widgit['state'] = 'disabled'
        else: 
            widgit['state'] = 'normal'

    def anodeWidgit(self): 
        """
        Function places a slider to set drift distance to anode in GENERAL frame. 
        """ 
        distance = tk.DoubleVar()
        distance.set(self.DISTANCE)
        
        slider = tk.Scale(self.general, variable = distance, from_ = 0, to = 3.53, orient = "horizontal", resolution = 0.01, length = 200)
        
        label = tk.Label(self.general, text = "Drift Distance (m)")
        label.grid(row = 1, column = 0)
        slider.grid(row = 1, column = 1, columnspan = 3)
        

    def seedWidgit(self):
        """
        Creates the wigit to set random seed for simulation instead of using default random number. 
        """

        # text label 
        seedLabel = tk.Label(self.general, text = "Seed")
        seedLabel.grid(row = 0, column = 0)

        # variable set as random seed by default 
        seedVal = tk.DoubleVar() 
        seedVal.set(self.SEED)

        # entry field tied to seedVal variable but greyed out by default 
        seedEntry = tk.Entry(self.general, textvariable = seedVal, state = "disabled")
        seedEntry.grid(row = 0, column = 2)

        # button allows editing of default random seed to custom value 
        seedBtn = tk.Button(self.general, text = "Define Seed", command = lambda: self.setState(seedEntry))
        seedBtn.grid(row = 0, column = 1)


class OpenerGUI(defaultsGUI):
    
    def __init__(self):
        """
        Creates initial window, with a choice to either create or analyse data.
        """
            
        # title of window 
        window.title("DUNE LArTPC Simulator")
        window.geometry("500x350")

        # label for choices
        self.question = tk.Label(window, text = "Do you want to create new or analyse existing data?")
        self.question.grid(row = 1, column = 0, columnspan = 4, sticky = "nswe")
        
        # buttons corresponding to choices
        self.createBtn = tk.Button(window, text = "Create", command = self.createData)
        self.analyseBtn = tk.Button(window, text = "Analyse", command = self.analyseData)
        self.createBtn.grid(row = 2, column = 0, columnspan = 2, sticky ="nswe")
        self.analyseBtn.grid(row = 2, column = 2, columnspan = 2, sticky ="nswe")

        # cool graphics
        self.canvas = tk.Canvas(window, width = 500, height = 10)
        self.canvas.grid(row = 0, column = 0, columnspan = 4, sticky = "nswe")
        self.img = ImageTk.PhotoImage(Image.open("sn1987a.jpg"))
        self.canvas.create_image(100,35, anchor = "center", image = self.img)

        # formatting, giving row weights allows rows to expand to fill space
        window.grid_rowconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)
        window.grid_rowconfigure(2, weight=1)

    def createData(self):
        """
        Create new window object to deal with creating a new data set. Allows selection of variable to change during data
        set creation, e.g. lifetime, radioactivity or electronic noise. 
        """

        # edit window to display new widgets (irritating to have lots of windows open!)
        window.title("Select variable")
        self.question.destroy()
        self.createBtn.destroy()
        self.analyseBtn.destroy()

        # text in window 
        self.variableQ = tk.Label(window, text = "Select Independent Variable for Dataset")
        self.variableQ.grid(row = 1, column = 0, columnspan = 5)

        # radioselect variable  
        self.selection = tk.StringVar()
        self.selection.set("lifetime")

        # radioselect buttons 
        self.lifetimeBtn = tk.Radiobutton(window, variable = self.selection, value = "lifetime", text = "Lifetime")
        self.elecNoiseBtn = tk.Radiobutton(window, variable = self.selection, value = "electronic", text = "Electronic Noise")
        self.radioactivityBtn = tk.Radiobutton(window, variable = self.selection, value = "radioactive", text = "Radioactivity")
        self.lifetimeBtn.grid(row = 2, column = 1)
        self.elecNoiseBtn.grid(row = 2, column = 2)
        self.radioactivityBtn.grid(row = 2, column = 3)

        # create input fields for parameter space to be probed 
        self.spaceFrame = tk.LabelFrame(window, text = "Input Parameter Space")
        self.spaceFrame.grid(row = 3, column = 1)
        
        self.valuesLabel = tk.Label(self.spaceFrame, text = "Values:")
        self.valuesLabel.grid(row = 0, column = 0)

        self.vals = tk.StringVar()
        self.valuesEntry = tk.Entry(self.spaceFrame, textvariable = self.vals)
        self.valuesEntry.grid(row = 0, column = 1)

        self.acceptBtn = tk.Button(self.spaceFrame, text = "Accept", command = self.getParameterSpace)
        self.acceptBtn.grid(row = 1, column = 1)

        
    def getParameterSpace(self):
        """
        Function takes the user input to find the different values of independent variable to use when generating a new 
        dataset. 
        """

        # get what input and convert to an array
        self.parameter = self.selection.get() 
        
        try: 
            self.parameterSpace = [float(i) for i in self.vals.get().split(',')]

            # bring up full default simulation window as a class object call
            self.setupDefaultWindow()

        except: 
            messagebox.showwarning(title = "Error", message = "Please enter a comma deliminated list of floats")
    
    def analyseData(self): 
        """
        Create a new window object allowing the selection of an existing dataset for analysis with ML. 
        """

        pass 

# set up main window 
window = tk.Tk() 
initWin = OpenerGUI()
# create the window 
window.mainloop()