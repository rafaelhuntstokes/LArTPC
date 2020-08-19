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
        self.SEED               = np.random.randint(0,100) 
        self.DISTANCE           = 3.53   # m 
        self.TRANSDIFF          = 7.2e-4 # m^2 s^-1 
        self.LONGDIFF           = 12e-4  # m^2 s^-1
        self.ELECTRONIC_NOISE   = 5      # std in ADC counts 
        self.NUMBER_EVENTS      = 100    # number of events to simualate
        self.LIFETIME           = 50     # micro seconds 
        self.ARGON_Q_VALUE      = 0.6    # MeV
        self.ARGON_ACTIVITY     = 10     # decays per module per ms
        self.POTASSIUM_Q_VALUE  = 3.5    # MeV
        self.POTASSIUM_ACTIVITY = 1e-3   # decays per module per ms
        
        # delete all the current frame widgets 
        self.spaceFrame.destroy()
        self.optionsFrame.destroy()
        try: 
            # may not have been created
            self.isotopeFrame.destroy()
        except: 
            pass 

        # create frames for general, radioactivity and navigation settings
        self.general = tk.LabelFrame(window, text = "General Settings")
        self.navigation = tk.LabelFrame(window, text = "Navigation") 
        self.radioactivity = tk.LabelFrame(window, text = "Radioactivity Settings")
        self.general.grid(sticky = "nsew") 
        self.radioactivity.grid(sticky = "nsew")
        self.navigation.grid()

        # create widgits
        # GENERAL SETTINGS FRAME 
        self.seedWidgit()         # set seed 
        self.anodeWidgit()        # drift distance slider
        self.diffusionCoeffs()    # long and trans diffusion coeffs 
        self.electronics()        # electronic noise kernel STD
        self.events()             # number of events 
        self.lifetime()           # electron lifetime

        # RADIOACTIVITY FRAME
        self.setupRadioactive()   # create a frame for each isotope in program and populate with widgets 

        # NAVIGATION FRAME 
        self.navButtons()         # confirm and back buttons 

    def setupRadioactive(self): 
        """
        Function creates a sub frame for each radioactive isotope loaded into the program. This is hardcoded (for now...). 
        """

        # create frames 
        self.argonFrame = tk.LabelFrame(self.radioactivity, text = "Argon-39")
        self.potassiumFrame = tk.LabelFrame(self.radioactivity, text = "Potassium-42")

        # entry string variables
        arQ = tk.StringVar()
        kQ = tk.StringVar()
        arActiv = tk.StringVar()
        kActiv = tk.StringVar()
        kQ.set(self.POTASSIUM_Q_VALUE)
        arQ.set(self.ARGON_Q_VALUE)
        arActiv.set(self.ARGON_ACTIVITY)
        kActiv.set(self.POTASSIUM_ACTIVITY)

        # argon Q-value fields
        self.arQLabel = tk.Label(self.argonFrame, text = "Q-Value (MeV)")
        self.arQBtn = tk.Button(self.argonFrame, text = "Edit?", command = lambda: self.setState(self.arQEntry))
        self.arQEntry = tk.Entry(self.argonFrame, textvariable = arQ, state = "disabled")

        # potassium Q-value fields 
        self.kQLabel = tk.Label(self.potassiumFrame, text = "Q-Value (MeV)")
        self.kQBtn = tk.Button(self.potassiumFrame, text = "Edit?", command = lambda: self.setState(self.kQEntry))
        self.kQEntry = tk.Entry(self.potassiumFrame, textvariable = kQ, state = "disabled")

        # checks to see if activity is independent variable 
        self.arActivLabel = tk.Label(self.argonFrame, text = "Activity (mod^-1 ms^-1)")
        self.kActivLabel = tk.Label(self.potassiumFrame, text = "Activity (mod^-1 ms^-1")
        
        if self.parameter == "radioactive":
            # using a collection of if statements for each isiotope since easier to add a new block if more isotopes are added 
            if self.isoSelection.get() == "argon":
                # argon activity has been set as the independent variable 
                arActiv.set(self.parameterSpace)
                self.arActivBtn = tk.Label(self.argonFrame, text = "INDIE VAR")
                self.arActivEntry = tk.Entry(self.argonFrame, textvariable = arActiv, state = "disabled")

                # handle potassium 
                self.kActivBtn = tk.Button(self.potassiumFrame, text = "Edit?", command = lambda: self.setState(self.kActivEntry))
                self.kActivEntry = tk.Entry(self.potassiumFrame, textvariable = kActiv, state = "disabled")

            if self.isoSelection.get() == "potassium":
                # potassium activity has been set as the independent variable 
                kActiv.set(self.parameterSpace)
                self.kActivBtn = tk.Label(self.potassiumFrame, text = "INDIE VAR")
                self.kActivEntry = tk.Entry(self.potassiumFrame, textvariable = kActiv, state = "disabled")

                # handle argon 
                self.arActivBtn = tk.Button(self.argonFrame, text = "Edit?", command = lambda: self.setState(self.arActivEntry))
                self.arActivEntry = tk.Entry(self.argonFrame, textvariable = arActiv, state = "disabled")

        else: 
            # radioactivity isn't independent variable so allow activity to be specified
            self.arActivBtn = tk.Button(self.argonFrame, text = "Edit?", command = lambda: self.setState(self.arActivEntry))
            self.arActivEntry = tk.Entry(self.argonFrame, textvariable = arActiv, state = "disabled")
            self.kActivBtn = tk.Button(self.potassiumFrame, text = "Edit?", command = lambda: self.setState(self.kActivEntry))
            self.kActivEntry = tk.Entry(self.potassiumFrame, textvariable = kActiv, state = "disabled")
            
        # place frames
        self.argonFrame.grid(row = 0, column = 1)
        self.potassiumFrame.grid(row = 1, column = 1)

        # place widgets 
        self.arQLabel.grid(row = 0, column = 0)
        self.arQBtn.grid(row = 0, column = 1)
        self.arQEntry.grid(row = 0, column = 2)
        self.arActivLabel.grid(row = 1, column = 0)
        self.arActivBtn.grid(row = 1, column = 1)
        self.arActivEntry.grid(row = 1, column = 2)
        self.kQLabel.grid(row = 0, column = 0)
        self.kQBtn.grid(row = 0, column = 1)
        self.kQEntry.grid(row = 0, column = 2)
        self.kActivLabel.grid(row = 1, column = 0)
        self.kActivBtn.grid(row = 1, column = 1)
        self.kActivEntry.grid(row = 1, column = 2)
        
        # # create widgets 
        # arQ = tk.StringVar()
        # arQ.set(self.ARGON_Q_VALUE)
        # self.argonQLabel = tk.Label(self.argonFrame, text = "Q-Value (MeV)")
        # self.argonBtn = tk.Button(self.argonFrame, text = "Edit?", command = lambda: self.setState(self.argonQEntry))
        # self.argonQEntry = tk.Entry(self.argonFrame, textvariable = arQ, state = "disabled")
        
        # self.argonActivityLabel = tk.Label(self.argonFrame, text = "Activity (mod^-1 ms^-1)")
        # arActiv = tk.StringVar()
        # if self.parameter != "radioactive":
        #     arActiv.set(self.ARGON_ACTIVITY)
        #     self.argonActivityEntry = tk.Entry(self.argonFrame, textvariable = arActiv, state = "disabled")
        #     self.argonActivityBtn = tk.Button(self.argonFrame, text = "Edit?", command = lambda: self.setState(self.argonActivityEntry))
        # else:
        #     self.ARGON_ACTIVITY = self.parameterSpace 
        #     arActiv.set(self.ARGON_ACTIVITY)
        #     self.argonActivityBtn = tk.Label(self.argonFrame, text = "INDIE VAR")
        #     self.argonActivityEntry = tk.Entry(self.argonFrame, textvariable = arActiv, state = "disabled")
        
        # # place widgets 
        # self.argonQLabel.grid(row = 0, column = 0)
        # self.argonBtn.grid(row = 0, column = 1)
        # self.argonQEntry.grid(row = 0, column = 2)
        # self.argonActivityLabel.grid(row = 1, column = 0)
        # self.argonActivityBtn.grid(row = 1, column = 1)
        # self.argonActivityEntry.grid(row = 1, column = 2)

        # # POTASSIUM-42 
        # self.potassiumFrame = tk.LabelFrame(self.radioactivity, text = "Potassium-42")

        # # create widgets 
        # kQ = tk.StringVar()
        # kQ.set(self.POTASSIUM_Q_VALUE)
        # self.potassiumQLabel = tk.Label(self.potassiumFrame, text = "Q-Value (MeV)")
        # self.potassiumBtn = tk.Button(self.potassiumFrame, text = "Edit?", command = lambda: self.setState(self.potassiumQEntry))
        # self.potassiumQEntry = tk.Entry(self.potassiumFrame, textvariable = kQ, state = "disabled")

        # self.potassiumActivityLabel = tk.Label(self.potassiumFrame, text = "Activity (mod^-1 ms^-1)")
        # kActiv = tk.StringVar()
        # if self.parameter != ""
        # kActiv.set(self.POTASSIUM_ACTIVITY)
        
        
        # self.potassiumActivityEntry = tk.Entry(self.potassiumFrame, textvariable = kActiv, state = "disabled")
        # self.potassiumActivityBtn = tk.Button(self.potassiumFrame, text = "Edit?", command = lambda: self.setState(self.potassiumActivityEntry))

        # # place widegts 
        # self.potassiumQLabel.grid(row = 0, column = 0)
        # self.potassiumBtn.grid(row = 0, column = 1)
        # self.potassiumQEntry.grid(row = 0, column = 2)
        # self.potassiumActivityLabel.grid(row = 1, column = 0)
        # self.potassiumActivityBtn.grid(row = 1, column = 1)
        # self.potassiumActivityEntry.grid(row = 1, column = 2)

        # # place frames
        # self.argonFrame.grid(row = 0, column = 1)
        # self.potassiumFrame.grid(row = 1, column = 1)

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
        self.radioactivity.destroy()
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
        self.eventsLabel.grid(row = 6, column = 0)

        number = tk.IntVar()
        number.set(self.NUMBER_EVENTS)

        self.eventSlide = tk.Scale(self.general, variable = number, from_ = 1, to = 10000, orient = "horizontal", length = 150, resolution = 50)
        self.eventSlide.grid(row = 6, column = 1, columnspan = 3)

    def lifetime(self):
        """
        Creates widget to input lifetime, unless set as independent variable, in which case shows previously
        specified values.
        """

        self.lifeLabel = tk.Label(self.general, text = "Lifetime (ms)")
        self.lifeLabel.grid(row = 5, column = 0)

        lifeVar = tk.StringVar()
        lifeVar.set(self.LIFETIME)

        self.lifeEntry = tk.Entry(self.general, textvariable = lifeVar, state = "disabled", width = 10)
        self.lifeEntry.grid(row = 5, column = 2)

        if self.parameter != "lifetime": 
            # allow user to set the values 
            self.lifeBtn = tk.Button(self.general, text = "Edit?", command = lambda: self.setState(self.lifeEntry))
            self.lifeBtn.grid(row = 5, column = 1)

        else: 
            # user cannot set lifetime as already specified 
            self.LIFETIME = self.parameterSpace
            lifeVar.set(self.LIFETIME)

            self.lifeInfo = tk.Label(self.general, text = "INDIE VAR") 
            self.lifeInfo.grid(row = 5, column = 1)
        
    def electronics(self): 
        """
        Widgit lets you set set standard deviation of gaussian blur for electronic noise response. Checks if electronic noise 
        is the independent variable - if yes, fills in the values previously given. 
        """

        self.elecLabel = tk.Label(self.general, text = "Electronic Noise STD (ADC)")
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

            self.elecInfo = tk.Label(self.general, text = "INDIE VAR")
            self.elecInfo.grid(row = 4, column = 1)

        self.elecEntry = tk.Entry(self.general, textvariable = elecNoise, state = "disabled", width = 10)
        self.elecEntry.grid(row = 4, column = 2)

    def diffusionCoeffs(self):
        """
        Creates the widgit for displaying/altering the diffusion coefficients.
        """

        transdiff = tk.DoubleVar()
        longdiff  = tk.DoubleVar()

        transdiff.set(self.TRANSDIFF)
        longdiff.set(self.LONGDIFF)

        self.transLabel = tk.Label(self.general, text = "Longitudinal Diffusion Coefficient (m^2 / s)")
        self.longLabel  = tk.Label(self.general, text = "Transverse Diffusion Coefficient (m^2 / s)")
        self.transLabel.grid(row = 2, column = 0)
        self.longLabel.grid(row = 3, column = 0)

        self.transEntry = tk.Entry(self.general, textvariable = transdiff, state = "disabled", width = 10)
        self.longEntry  = tk.Entry(self.general, textvariable = longdiff, state = "disabled", width = 10)
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
        
        slider = tk.Scale(self.general, variable = distance, from_ = 0, to = 3.53, orient = "horizontal", resolution = 0.01, length = 150)
        
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
        seedEntry = tk.Entry(self.general, textvariable = seedVal, state = "disabled", width = 10)
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
        #window.geometry("600x300")

        # cool graphics
        self.canvas = tk.Canvas(window, width = 500, height = 50)
        self.canvas.grid(row = 0, column = 0, columnspan = 4, sticky = "nswe")
        self.img = ImageTk.PhotoImage(Image.open("sn1987a.jpg"))
        self.canvas.create_image(100,35, anchor = "center", image = self.img)

        # label for choices
        self.question = tk.Label(window, text = "Do you want to create new or analyse existing data?")
        self.question.grid(row = 1, column = 0, columnspan = 4, rowspan = 2, sticky = "nswe")
        
        # buttons corresponding to choices
        self.createBtn = tk.Button(window, text = "Create", command = self.createData)
        self.analyseBtn = tk.Button(window, text = "Analyse", command = self.analyseData)
        self.createBtn.grid(row = 3, column = 0, columnspan = 2, sticky ="nswe")
        self.analyseBtn.grid(row = 3, column = 2, columnspan = 2, sticky ="nswe")

        # formatting, giving row weights allows rows to expand to fill space
        window.grid_rowconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)
        window.grid_rowconfigure(2, weight=1)
        window.grid_columnconfigure(4, weight = 1)

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
        # self.variableQ = tk.Label(window, text = "Select Independent Variable for Dataset")
        # self.variableQ.grid(row = 1, column = 0, columnspan = 5)

        # radioselect variable  
        self.selection = tk.StringVar()
        self.selection.set("lifetime")

        # create frame for the options 
        self.optionsFrame = tk.LabelFrame(window, text = "Independent Variables")
        self.optionsFrame.grid(row = 1, column = 0, columnspan = 5)

        # radioselect buttons 
        self.lifetimeBtn = tk.Radiobutton(self.optionsFrame, variable = self.selection, value = "lifetime", text = "Lifetime")
        self.elecNoiseBtn = tk.Radiobutton(self.optionsFrame, variable = self.selection, value = "electronic", text = "Electronic Noise")
        self.radioactivityBtn = tk.Radiobutton(self.optionsFrame, variable = self.selection, value = "radioactive", text = "Radioactivity")
        self.lifetimeBtn.grid(row = 0, column = 0)
        self.elecNoiseBtn.grid(row = 0, column = 1)
        self.radioactivityBtn.grid(row = 0, column = 2)

        # bind radioactivity button selection to click event that will open up new frame 
        # allowing selection of desired isotope
        self.radioactivityBtn.bind("<Button-1>", self.isotopeChoice)

        # create input fields for parameter space to be probed 
        self.spaceFrame = tk.LabelFrame(window, text = "Input Parameter Space")
        self.spaceFrame.grid(row = 2, column = 0, columnspan = 5, sticky = "n")
        
        self.valuesLabel = tk.Label(self.spaceFrame, text = "Values:")
        self.valuesLabel.grid(row = 0, column = 0)

        self.vals = tk.StringVar()
        self.valuesEntry = tk.Entry(self.spaceFrame, textvariable = self.vals)
        self.valuesEntry.grid(row = 0, column = 1)

        self.acceptBtn = tk.Button(self.spaceFrame, text = "Accept", command = self.getParameterSpace)
        self.acceptBtn.grid(row = 1, column = 1)

        self.backBtn2 = tk.Button(self.spaceFrame, text = "Back", command = self.returnToStart)
        self.backBtn2.grid(row = 1, column = 2)

    def isotopeChoice(self, event):
        """
        Event callback function which creates a new frame in independent variable selection window, allowing user to 
        specify which radioactive isotope's activity to vary.
        """

        # create frame and reposition 
        self.isotopeFrame = tk.LabelFrame(window, text = "Select Isotope")
        self.isotopeFrame.grid(row = 2, column = 0, columnspan = 5)
        self.spaceFrame.grid(row = 3, column = 0, columnspan = 5)

        # add radioselect buttons for isotopes 
        self.isoSelection = tk.StringVar()
        self.isoSelection.set("argon")
        self.arSelec = tk.Radiobutton(self.isotopeFrame, value = "argon", variable = self.isoSelection, text = "Ar-39")
        self.kSelec = tk.Radiobutton(self.isotopeFrame, value = "potassium", variable = self.isoSelection, text = "K-42")
        self.arSelec.grid(row = 0, column = 0)
        self.kSelec.grid(row = 0, column = 1)

    def returnToStart(self): 
        """
        Returns from independent variable selection screen to analyse/create data screen. 
        """

        # destroy widgets 
        self.optionsFrame.destroy()
        self.spaceFrame.destroy()

        # recreate screen 
        self.__init__()

    def getParameterSpace(self):
        """
        Function takes the user input to find the different values of independent variable to use when generating a new 
        dataset. 
        """

        # get what input and convert to an array
        self.parameter = self.selection.get() 
        success = False 
        try: 
            self.parameterSpace = [float(i) for i in self.vals.get().split(',')]
            success = True

        except: 
            messagebox.showwarning(title = "Error", message = "Please enter a comma deliminated list of floats")
    
        if success:
            # bring up full default simulation window as a class object call
            self.setupDefaultWindow()

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