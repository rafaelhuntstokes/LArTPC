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
        self.SEED                  = np.random.randint(0,100) 
        self.DISTANCE              = 3.53   # m 
        self.TRANSDIFF             = 7.2e-4 # m^2 s^-1 
        self.LONGDIFF              = 12e-4  # m^2 s^-1
        self.ELECTRONIC_NOISE      = 5      # std in ADC counts 
        self.NUMBER_EVENTS         = 100    # number of events to simualate
        self.LIFETIME              = 50     # micro seconds 
        self.ARGON_Q_VALUE         = 0.6    # MeV
        self.ARGON_ACTIVITY        = 10     # decays per module per ms
        self.POTASSIUM_Q_VALUE     = 3.5    # MeV
        self.POTASSIUM_ACTIVITY    = 1e-3   # decays per module per ms
        self.RADIOACTIVE_STEP_SIZE = 0.5    # cm (?) step size for depositing radioactive energy along trajectories
        self.EPOCHS                = 20     # default number of epochs to use in ML training 
        self.BATCH                 = 32     # default batch size for ML training 
        self.TRAIN                 = 0.6    # default % data used to train model 
        self.VALIDATE              = 0.2    # default % data used to validate model 
        self.TEST                  = 0.2    # default % data used to test model 

        # flag dict to determine which options to apply to sim 
        self.SETTINGS = {"MACHINE_LEARNING": True, "RADIOACTIVITY_MASTER": True, "RADIOACTIVE_SMEAR": True, "ISOTOPE_ARGON": True, 
                         "ISOTOPE_POTASSIUM": True, "TRANS_DIFFUSION": True, "LONG_DIFFUSION": True,
                         "ELECTRONIC_NOISE": True, "LIFETIME": True, "DATA_LOC": "./images", "RESULTS_LOC": "./results"}

        # delete all the current frame widgets 
        self.spaceFrame.destroy()
        self.optionsFrame.destroy()
        try: 
            # may not have been created
            self.isotopeFrame.destroy()
        except: 
            pass 
        
        # change window heading 
        window.title("Simulation Settings")

        # create frames for general, radioactivity, machine learning, saving files and navigation settings
        self.general = tk.LabelFrame(window, text = "General Settings")
        self.radioactivity = tk.LabelFrame(window, text = "Radioactivity Settings")
        self.machine = tk.LabelFrame(window, text = "Machine Learning Settings")
        self.saving = tk.LabelFrame(window, text = "Saving Data")
        self.navigation = tk.LabelFrame(window, text = "Navigation") 

        self.general.grid(sticky = "nsew") 
        self.radioactivity.grid(sticky = "nsew")
        self.machine.grid(sticky = "nsew")
        self.saving.grid(sticky = "nsew")
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
        self.setupRadioactiveMasterBtn() # add toggle button to add/remove all radioactive simulations 
        self.setupRadioactiveSmear()     # create a frame to select point deposition or smearing behaviour of radioactive decays 
        self.setupRadioactiveIsotopes()  # create a frame for each isotope in program and populate with widgets 

        # MACHINE LEARNING FRAME
        self.machineSettings() # number of epochs, batch size and train/valid/test split

        # SAVE DATA FRAME
        self.saveData() # add widgets to specify the location to save generated data and results 

        # NAVIGATION FRAME 
        self.navButtons()         # confirm and back buttons 

    def changeButtonState(self, frame, Button, flag):
        """
        Function changes a button text and colour when clicked, switches associated Boolean value in self.SETTINGS, and will enable
        or disable an entire frame of widgets depending on the button calling it.
        """

        # change colour, text and state 
        if Button["text"] == "ON":
            Button["text"] = "OFF"
            Button["bg"] = "red"
            self.SETTINGS[flag] = False

            # disable all other widgets in frame
            for child in frame.winfo_children():
                # frame widgets don't support "state" 
                if child.winfo_class() != "Labelframe":
                    child.configure(state = "disabled") 
                else: 
                    # if find subframe as a child, find the children of subframe and disable them 
                    for recursiveChild in child.winfo_children():
                        recursiveChild.configure(state = "disabled")
                        # change colour and text of button in sub frame 
                        if recursiveChild.winfo_class() == "Button":
                            # make sure it's a toggle button
                            if recursiveChild["text"] != "Edit?":
                                recursiveChild.configure(text = "OFF")
                                recursiveChild.configure(bg = "red") 

            # re-enable the flag button 
            Button["state"] = "normal"
        
        else: 
            Button["text"] = "ON"
            Button["bg"] = "green"
            self.SETTINGS[flag] = True
        
            # enable all other widgets in frame
            for child in frame.winfo_children():
                if child.winfo_class() != "Labelframe":
                    child.configure(state = "normal")
                    # stop entry widgets being enabled by default since we want them only to be editable 
                    # when edit button is pressed 
                    if child.winfo_class() == "Entry": 
                        child.configure(state = "disabled")
                else: 
                    for recursiveChild in child.winfo_children():
                        recursiveChild.configure(state = "normal")
                        if recursiveChild.winfo_class() == "Entry": 
                            recursiveChild.configure(state = "disabled")
                        # change colour and text of button in sub frame 
                        if recursiveChild.winfo_class() == "Button":
                            # make sure it's a toggle button
                            if recursiveChild["text"] != "Edit?":
                                recursiveChild.configure(text = "ON")
                                recursiveChild.configure(bg = "green") 
        
        # if ML settings switched on/off, enable/disable save results entry (no ML, no results to save)
        if flag == "MACHINE_LEARNING": 
            if Button["text"] == "ON":
                # enable save results 
                self.resultsPathEntry["state"] = "normal"
                self.resultsPath.set(self.SETTINGS["RESULTS_LOC"])
            else: 
                # disable results path
                self.resultsPath.set("NO ML RESULTS")
                self.resultsPathEntry["state"] = "disabled"

    def saveData(self):
        """
        Adds widgets to allow user to specify the location to save generated data and results. 
        """

        # explanatory text
        self.explanationSaveTxt = tk.Label(self.saving, text = "Please specify the location to save generated images and results.")
        self.explanationSaveTxt.grid(columnspan = 2)

        # labels and entry fields for image files and results
        self.imPath = tk.StringVar()
        self.resultsPath = tk.StringVar()
        self.imPath.set(self.SETTINGS["DATA_LOC"])
        self.resultsPath.set(self.SETTINGS["RESULTS_LOC"])
        self.imagePathLabel = tk.Label(self.saving, text = "Image Save Path: ")
        self.imagePathEntry = tk.Entry(self.saving, textvariable = self.imPath)
        self.resultsPathLabel = tk.Label(self.saving, text = "Results Save Path: ")
        self.resultsPathEntry = tk.Entry(self.saving, textvariable = self.resultsPath)

        # place widgets 
        self.imagePathLabel.grid(row = 1, column = 0)
        self.imagePathEntry.grid(row = 1, column = 1)
        self.resultsPathLabel.grid(row = 2, column = 0)
        self.resultsPathEntry.grid(row = 2, column = 1)

    def machineSettings(self): 
        """
        Function populates the ML frame with settings widgets to allow control of learning rate, (+other settings?).
        """
        
        # button to turn ML settings on or OFF
        self.machineOnBtn = tk.Button(self.machine, text = "ON", bg = "green", command = lambda: self.changeButtonState(self.machine, self.machineOnBtn, "MACHINE_LEARNING"))
        self.machineOnBtn.grid(sticky = "ew")

        # create widgets 
        self.epochs = tk.StringVar()
        self.batch = tk.StringVar()
        self.train = tk.StringVar()
        self.valid = tk.StringVar()
        self.test = tk.StringVar()
        self.epochs.set(self.EPOCHS)
        self.batch.set(self.BATCH)
        self.train.set(self.TRAIN)
        self.valid.set(self.VALIDATE)
        self.test.set(self.TEST)

        self.description = tk.Label(self.machine, text = "CNN trained and tested on data using Adam optimiser.")
        self.epochLabel = tk.Label(self.machine, text = "Epochs")
        self.epochEntry = tk.Entry(self.machine, textvariable = self.epochs, width = 5)
        self.batchLabel = tk.Label(self.machine, text = "Batch Size")
        self.batchEntry = tk.Entry(self.machine, textvariable = self.batch, width = 5)
        self.trainLabel = tk.Label(self.machine, text = "Train %")
        self.validLabel = tk.Label(self.machine, text = "Valid %")
        self.testLabel = tk.Label(self.machine, text = "Test %")
        self.trainEntry = tk.Entry(self.machine, textvariable = self.train, width = 5)
        self.validEntry = tk.Entry(self.machine, textvariable = self.valid, width = 5)
        self.testEntry = tk.Entry(self.machine, textvariable = self.test, width = 5)

        # place widgets 
        self.description.grid(row = 0, column = 1, columnspan = 6)
        self.epochLabel.grid(row = 1, column = 1)
        self.epochEntry.grid(row = 1, column = 2)
        self.batchLabel.grid(row = 2, column = 1)
        self.batchEntry.grid(row = 2, column = 2)
        self.trainLabel.grid(row = 3, column = 1)
        self.trainEntry.grid(row = 3, column = 2)
        self.validLabel.grid(row = 3, column = 3)
        self.validEntry.grid(row = 3, column = 4)
        self.testLabel.grid(row = 3, column = 5)
        self.testEntry.grid(row = 3, column = 6)

    def setupRadioactiveMasterBtn(self):
        """
        Function creates a toggle button to enable/disable ALL radioactivity effects
        """

        self.radioactiveMasterBtn = tk.Button(self.radioactivity, text = "ON", bg = "green", command = lambda: self.changeButtonState(self.radioactivity, self.radioactiveMasterBtn, "RADIOACTIVITY_MASTER"))
        self.radioactiveMasterBtn.grid(row = 0, column = 0, sticky = "ew")
        
        # check if radioactive isotope has been selected as independent variable 
        if self.parameter == "radioactive":
            
            # cannot toggle all of the radioactivity settings off 
            self.radioactiveMasterBtn["state"] = "disabled"

    def setupRadioactiveSmear(self):
        """
        Creates frame and widgets to allow user to turn smearing effects on or off and select step size of energy 
        deposition if turned on. 
        """

        # create subframe 
        self.radioactiveSmearFrame = tk.LabelFrame(self.radioactivity, text = "Radioactive Beta Smearing")

        # create widgets 
        self.stepSize = tk.StringVar()
        self.stepSize.set(self.RADIOACTIVE_STEP_SIZE)
        self.radioactiveSmearBtn = tk.Button(self.radioactiveSmearFrame, text = "ON", bg = "green", command = lambda: self.changeButtonState(self.radioactiveSmearFrame, self.radioactiveSmearBtn, "RADIOACTIVE_SMEAR"))
        self.radioactiveSmearLabel = tk.Label(self.radioactiveSmearFrame, text = "Step Size (cm):")
        self.radioactiveSmearEdit = tk.Button(self.radioactiveSmearFrame, text = "Edit?", command = lambda: self.setState(self.radioactiveSmearEntry))
        self.radioactiveSmearEntry = tk.Entry(self.radioactiveSmearFrame, textvariable = self.stepSize, state = "disabled")

        # place widgets 
        self.radioactiveSmearFrame.grid(row = 1, column = 0, sticky = "ew")
        self.radioactiveSmearBtn.grid(row = 0, column = 0)
        self.radioactiveSmearLabel.grid(row = 0, column = 1)
        self.radioactiveSmearEdit.grid(row = 0, column = 2)
        self.radioactiveSmearEntry.grid(row = 0, column = 3)

        self.radioactiveSmearFrame.columnconfigure(1, weight = 1)

    def setupRadioactiveIsotopes(self): 
        """
        Function creates a sub frame for each radioactive isotope loaded into the program. This is hardcoded (for now...). 
        """

        # create frames 
        self.argonFrame = tk.LabelFrame(self.radioactivity, text = "Argon-39")
        self.potassiumFrame = tk.LabelFrame(self.radioactivity, text = "Potassium-42")

        # entry string variables
        self.arQ = tk.StringVar()
        self.kQ = tk.StringVar()
        self.arActiv = tk.StringVar()
        self.kActiv = tk.StringVar()
        self.kQ.set(self.POTASSIUM_Q_VALUE)
        self.arQ.set(self.ARGON_Q_VALUE)
        self.arActiv.set(self.ARGON_ACTIVITY)
        self.kActiv.set(self.POTASSIUM_ACTIVITY)

        # argon Q-value fields
        self.arQLabel = tk.Label(self.argonFrame, text = "Q-Value (MeV)")
        self.arQBtn = tk.Button(self.argonFrame, text = "Edit?", command = lambda: self.setState(self.arQEntry))
        self.arQEntry = tk.Entry(self.argonFrame, textvariable = self.arQ, state = "disabled")

        # potassium Q-value fields 
        self.kQLabel = tk.Label(self.potassiumFrame, text = "Q-Value (MeV)")
        self.kQBtn = tk.Button(self.potassiumFrame, text = "Edit?", command = lambda: self.setState(self.kQEntry))
        self.kQEntry = tk.Entry(self.potassiumFrame, textvariable = self.kQ, state = "disabled")

        # checks to see if activity is independent variable 
        self.arActivLabel = tk.Label(self.argonFrame, text = "Activity (mod^-1 ms^-1)")
        self.kActivLabel = tk.Label(self.potassiumFrame, text = "Activity (mod^-1 ms^-1)")

        # add on/off button for simulating the isotope
        self.arOnBtn = tk.Button(self.argonFrame, text = "ON", bg = "green", command = lambda: self.changeButtonState(self.argonFrame, self.arOnBtn, "ISOTOPE_ARGON"))
        self.kOnBtn = tk.Button(self.potassiumFrame, text = "ON", bg = "green", command = lambda: self.changeButtonState(self.potassiumFrame, self.kOnBtn, "ISOTOPE_POTASSIUM"))

        if self.parameter == "radioactive":
            # using a collection of if statements for each isiotope since easier to add a new block if more isotopes are added 
            if self.isoSelection.get() == "argon":
                # argon activity has been set as the independent variable 
                # grey out argon ON/OFF button since it must be on 
                self.arOnBtn["state"] = "disabled"

                self.arActiv.set(self.parameterSpace)
                self.arActivBtn = tk.Label(self.argonFrame, text = "INDIE VAR")
                self.arActivEntry = tk.Entry(self.argonFrame, textvariable = self.arActiv, state = "disabled")

                # handle potassium 
                self.kActivBtn = tk.Button(self.potassiumFrame, text = "Edit?", command = lambda: self.setState(self.kActivEntry))
                self.kActivEntry = tk.Entry(self.potassiumFrame, textvariable = self.kActiv, state = "disabled")

            if self.isoSelection.get() == "potassium":
                # potassium activity has been set as the independent variable 
                # grey out argon ON/OFF button since it must be on 
                self.kOnBtn["state"] = "disabled"

                self.kActiv.set(self.parameterSpace)
                self.kActivBtn = tk.Label(self.potassiumFrame, text = "INDIE VAR")
                self.kActivEntry = tk.Entry(self.potassiumFrame, textvariable = self.kActiv, state = "disabled")

                # handle argon 
                self.arActivBtn = tk.Button(self.argonFrame, text = "Edit?", command = lambda: self.setState(self.arActivEntry))
                self.arActivEntry = tk.Entry(self.argonFrame, textvariable = self.arActiv, state = "disabled")

        else: 
            # radioactivity isn't independent variable so allow activity to be specified
            self.arActivBtn = tk.Button(self.argonFrame, text = "Edit?", command = lambda: self.setState(self.arActivEntry))
            self.arActivEntry = tk.Entry(self.argonFrame, textvariable = self.arActiv, state = "disabled")
            self.kActivBtn = tk.Button(self.potassiumFrame, text = "Edit?", command = lambda: self.setState(self.kActivEntry))
            self.kActivEntry = tk.Entry(self.potassiumFrame, textvariable = self.kActiv, state = "disabled")
            
        # place frames
        self.argonFrame.grid(row = 2, column = 0)
        self.potassiumFrame.grid(row = 3, column = 0)

        # place widgets 
        self.arOnBtn.grid(row = 0, column = 0, sticky = "ew")
        self.arQLabel.grid(row = 0, column = 1)
        self.arQBtn.grid(row = 0, column = 2)
        self.arQEntry.grid(row = 0, column = 3)
        self.arActivLabel.grid(row = 1, column = 1)
        self.arActivBtn.grid(row = 1, column = 2)
        self.arActivEntry.grid(row = 1, column = 3)
        self.kOnBtn.grid(row = 0, column = 0, sticky = "ew")
        self.kQLabel.grid(row = 0, column = 1)
        self.kQBtn.grid(row = 0, column = 2)
        self.kQEntry.grid(row = 0, column = 3)
        self.kActivLabel.grid(row = 1, column = 1)
        self.kActivBtn.grid(row = 1, column = 2)
        self.kActivEntry.grid(row = 1, column = 3)
        
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
        self.machine.destroy()
        self.saving.destroy()
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
        self.eventsLabel.grid(row = 2, column = 0)

        number = tk.IntVar()
        number.set(self.NUMBER_EVENTS)

        self.eventSlide = tk.Scale(self.general, variable = number, from_ = 50, to = 10000, orient = "horizontal", length = 150, resolution = 50)
        self.eventSlide.grid(row = 2, column = 1, columnspan = 3)

    def lifetime(self):
        """
        Creates widget to input lifetime, unless set as independent variable, in which case shows previously
        specified values.
        """

        # add ON/OFF button by creating a sub frame for the option to be toggled on/off
        # otherwise the changeButtonState would get every child in self.general to toggle! 
        self.lifetime_frame = tk.Frame(self.general)
        self.lifetime_frame.grid(row = 6, column = 0, columnspan = 4, sticky = "ew")
        self.lifetimeOnBtn = tk.Button(self.lifetime_frame, text = "ON", bg = "green", command = lambda: self.changeButtonState(self.lifetime_frame, self.lifetimeOnBtn, "LIFETIME"))
        self.lifetimeOnBtn.grid(row = 0, column = 0)
        self.lifeLabel = tk.Label(self.lifetime_frame, text = "Lifetime (ms)")
        self.lifeLabel.grid(row = 0, column = 1)

        self.lifeVar = tk.StringVar()
        self.lifeVar.set(self.LIFETIME)

        self.lifeEntry = tk.Entry(self.lifetime_frame, textvariable = self.lifeVar, state = "disabled", width = 10)
        self.lifeEntry.grid(row = 0, column = 3, sticky= "e")

        if self.parameter != "lifetime": 
            # allow user to set the values 
            self.lifeBtn = tk.Button(self.lifetime_frame, text = "Edit?", command = lambda: self.setState(self.lifeEntry))
            self.lifeBtn.grid(row = 0, column = 2)

        else: 
            # user cannot set lifetime as already specified 
            # lifetime cannot be switched off 
            self.lifetimeOnBtn["state"] = "disabled"
            self.LIFETIME = self.parameterSpace
            self.lifeVar.set(self.LIFETIME)

            self.lifeInfo = tk.Label(self.lifetime_frame, text = "INDIE VAR") 
            self.lifeInfo.grid(row = 0, column = 2)

        # position neatly 
        self.lifetime_frame.columnconfigure(1, weight = 1)
        
    def electronics(self): 
        """
        Widget lets you set set standard deviation of gaussian blur for electronic noise response. Checks if electronic noise 
        is the independent variable - if yes, fills in the values previously given. 
        """

        # create sub frame for toggling settings on/off
        self.electronics_frame = tk.Frame(self.general)
        self.electronics_frame.grid(row = 5, column = 0, columnspan = 4, sticky = "ew")

        # create toggle button 
        self.electronicsOnBtn = tk.Button(self.electronics_frame, text = "ON", bg = "green", command = lambda: self.changeButtonState(self.electronics_frame, self.electronicsOnBtn, "ELECTRONIC_NOISE"))
        self.electronicsOnBtn.grid(row = 0, column = 0)
        self.elecLabel = tk.Label(self.electronics_frame, text = "Electronic Noise STD (ADC)")
        self.elecLabel.grid(row = 0, column = 1)

        elecNoise = tk.DoubleVar()

        if self.parameter != "electronic":
            # electronic noise is a dependent variable to be specified as a constant 
            elecNoise = tk.DoubleVar()
            elecNoise.set(self.ELECTRONIC_NOISE)

            self.elecBtn = tk.Button(self.electronics_frame, text = "Edit?", command = lambda: self.setState(self.elecEntry))
            self.elecBtn.grid(row = 0, column = 2)
        
        else: 
            # electronic noise is the independent variable, with values already set. Fill widget with these values. 
            # can't toggle independent variable on/off
            self.electronicsOnBtn["state"] = "disabled"
            self.ELECTRONIC_NOISE = self.parameterSpace
            elecNoise.set(self.ELECTRONIC_NOISE)

            self.elecInfo = tk.Label(self.electronics_frame, text = "INDIE VAR")
            self.elecInfo.grid(row = 0, column = 2)

        self.elecEntry = tk.Entry(self.electronics_frame, textvariable = elecNoise, state = "disabled", width = 10)
        self.elecEntry.grid(row = 0, column = 3)

        # positioning neatly 
        self.electronics_frame.columnconfigure(1, weight = 1)

    def diffusionCoeffs(self):
        """
        Creates the widgit for displaying/altering the diffusion coefficients.
        """

        # create sub-frames for toggle buttons 
        self.longDiffFrame = tk.Frame(self.general)
        self.transDiffFrame = tk.Frame(self.general)
        self.longDiffFrame.grid(row = 4, column = 0, columnspan = 3, sticky = "ew")
        self.transDiffFrame.grid(row = 3, column = 0, columnspan = 3, sticky = "ew")
        
        # set textvariables used to track diffusion coeff values 
        transdiff = tk.DoubleVar()
        longdiff  = tk.DoubleVar()
        transdiff.set(self.TRANSDIFF)
        longdiff.set(self.LONGDIFF)

        # create the toggle buttons 
        self.longDiffBtn = tk.Button(self.longDiffFrame, text = "ON", bg = "green", command = lambda: self.changeButtonState(self.longDiffFrame, self.longDiffBtn, "LONG_DIFFUSION"))
        self.transDiffBtn = tk.Button(self.transDiffFrame, text = "ON", bg = "green", command = lambda: self.changeButtonState(self.transDiffFrame, self.transDiffBtn, "TRANS_DIFFUSION"))
        self.longDiffBtn.grid(row = 0, column = 0, sticky = "ew")
        self.transDiffBtn.grid(row = 0, column = 0, sticky = "ew")

        # create other widgets 
        self.transLabel = tk.Label(self.transDiffFrame, text = "Transverse Diffusion Coefficient (m^2 / s)")
        self.longLabel  = tk.Label(self.longDiffFrame, text = "Longitudinal Diffusion Coefficient (m^2 / s)")
        self.transLabel.grid(row = 0, column = 1, sticky = "ew")
        self.longLabel.grid(row = 0, column = 1, sticky = "ew")

        self.transEntry = tk.Entry(self.transDiffFrame, textvariable = transdiff, state = "disabled", width = 10)
        self.longEntry  = tk.Entry(self.longDiffFrame, textvariable = longdiff, state = "disabled", width = 10)
        self.transEntry.grid(row = 0, column = 3, sticky = tk.E)
        self.longEntry.grid(row = 0, column = 3, sticky = tk.E)

        self.transBtn = tk.Button(self.transDiffFrame, text = "Edit?", command = lambda: self.setState(self.transEntry))
        self.longBtn  = tk.Button(self.longDiffFrame, text = "Edit?", command = lambda: self.setState(self.longEntry))
        self.transBtn.grid(row = 0, column = 2, sticky = "ew")
        self.longBtn.grid(row = 0, column = 2, sticky = "ew")

        # positioning neatly 
        self.transDiffFrame.columnconfigure(1, weight = 1)

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
        
        slider = tk.Scale(self.general, variable = distance, from_ = 0.01, to = 3.53, orient = "horizontal", resolution = 0.01, length = 150)
        
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

        # bind clicks to other options to remove the isotope selection widget if it exists
        self.lifetimeBtn.bind("<Button-1>", self.removeIsotopePanel)
        self.elecNoiseBtn.bind("<Button-1>", self.removeIsotopePanel)

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

    def removeIsotopePanel(self, event):
        """
        Function removes the isotope selection panel if it exists when elec. noise or lifetime buttons clicked.
        """

        try: 
            # destroy frame
            self.isotopeFrame.destroy()
        except:
            # it may not exist 
            pass

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