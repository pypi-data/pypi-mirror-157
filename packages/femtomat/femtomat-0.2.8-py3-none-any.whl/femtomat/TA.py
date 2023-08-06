import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets

from femtomat.functions import nearest, svd_reconstruction_E15, rmse_special, k_opt

class TA_Pre:
    '''
    A class to perform TA data preprocessing before analysis. This includes data trimming, background subtraction and chirp correction.
    '''
    def __init__(self, Data):
        '''
        Upon initialization the ``check_w_orientation`` function is called, to ensure that the wavelengths are in numberical order. The raw data is then separated into TA data ``D`` and its corresponding wavelengths ``w`` and timedelays ``t`` .
        
        :param Data: A numpy object in the form of the raw TA data without any preprocessing. i.e. ``TA_Pre(np.loadtxt('sample_800nm_5nJ.txt'))`` .
        
        :attributes TA Data: 
                    * self.Data - Raw data is it was uploaded after orientation change.
                    * self.D - Data after being preprocessed.  
                    * self.w - Wavelengths corresponding to data.
                    * self.t - Timedelays correcponding to data.
        '''
        self.Data = Data
        self.check_w_orientation()
        self.D = Data[1:,1:]
        self.w = Data[1:,0]
        self.t = Data[0,1:]
        self.Chirp_UI()
    
    #update every time we change something
    def update(self, wRange, tRange, ARange, neg_sub, y0, A, tau, x0):
        '''
        An update function which links the input widgets to the processing and plotting functions.
        
        :param wRange: Contains a tuple with the wavelength range at which the TA data is trimmed.
        :param tRange: Contains a tuple with the timedelay range at wich the TA is displayed.
        :param Arange: Contains a tuple with the amplitude range at wich the TA is displayed.
        :param neg_sub: The timedelays below which the averaging for the background subtraction is taken.
        :param Chirp: The four parameters used in the chirp correction proceedure.
        
        All the input parameters become attributes of the object and can be accessed at any time.
        
        :attributes Data trimming:
                    * self.wRange - Wavelength range specified for 'clean' spectra.
                    * self.neg_sub - Time below which the background is calculated.
                    
        :attributes Chirp correction:
                    * self.tRange - Time range plotted to manually check goodness of chipr correction.
                    * self.ARange - Amplitude range plotted to manually check goodness of chipr correction.
                    * self.Chirp - Parameters of the sample specific exponential function used to correct for the chirp.
        '''
        self.wRange, self.tRange, self.ARange = wRange, tRange, ARange
        self.neg_sub = neg_sub
        self.Chirp = [y0,A,tau,x0]
        self.cut_to_range()
        self.chirp_correction()
        self.plot_range()
        self.plot_chirp()
    
    def check_w_orientation(self):
        '''
        A function which checks if the wavelengths are in numerical order and flips them (along with the data) if not.
        '''
        if (self.Data[2,0] > self.Data[-2,0]):
            self.Data = np.flip(self.Data,axis = 0)
            self.Data = np.vstack((self.Data[-1,:],self.Data[:-1,:]))
    
    #Cutting the data in the wavelength range
    def cut_to_range(self):
        '''
        Function which takes the clean data wavelength range ``wRange`` as specified by the user with the widget and cuts the data and wavelengths accordingly. The function also takes the mean of spectra at times less than the widget specified ``neg_sub`` value as a background and subreacts it from all the data as a first data cleaning step. Negative time subtraction is most udefull for removing pump scattering which is present at all times. 
        '''
        indl = nearest(self.Data[1:,0],self.wRange[0])
        indr = nearest(self.Data[1:,0],self.wRange[1])
        self.D = self.Data[indl:indr,1:]
        self.w = self.Data[indl:indr,0]
        sub = np.mean(self.D[:,:nearest(self.t,self.neg_sub)], axis = 1)
        self.D = (self.D.T-sub).T
    
    #Chirp correction function
    def chirp_correction(self):
        '''
        Since the white light pulse is chirped, meaning that the blue side of the white light distribution arrives at the sample before the red side, the time zeros of the rise of the signal is different for each wavelength. This wavelength dependant time zero can be approximated by an exponential function. This exponential is then used to create a new set of timedelays for each wavelength is a way that the rise of the signal is at time zero. The time-shifted signals are then interpolated back onto the origional timedelays and the data matrix is redefined.
        '''
        def func(x,y0,A,tau,x0):
            return y0 + A*np.exp(-(x-x0)/tau)
        td = np.zeros(self.D.shape)
        data_i = np.zeros(self.D.shape)
        for i in range(len(self.w)):
            for j in range(len(self.t)):
                td[i,j] = self.t[j] - func(self.w[i],*self.Chirp)
                data_i[i,:] = np.interp(self.t,td[i,:],self.D[i,:])
        self.D = data_i
        
    #Plot the spectra in order to find the range
    def plot_range(self):
        '''
        A function to plot all spectra in the TA data matrix such that the 'clean' part of the spectra can be defined by eye.
        '''
        plt.figure(figsize=(20,5))
        plt.title('Full Data Range for Cutting')
        plt.plot(self.w,self.D)
        plt.hlines(0,self.wRange[0]-20,self.wRange[1]+20, color = 'k')
        plt.vlines(self.wRange,self.ARange[0],self.ARange[1], color = 'k')
        plt.ylim(self.ARange[0],self.ARange[1])
        plt.xlim(self.wRange[0]-20,self.wRange[1]+20)
        plt.ylabel('\u0394A (mOD)')
        plt.xlabel('Wavelengths (nm)')
        
    #Plot the image and dynamics for chirp correction
    def plot_chirp(self):
        '''
        The dynamics around time zero are plotted first as a contour plot and then as a selection of dynamics to that the goodness of the chirp correction can be assessed and adjusted by eye.
        '''
        plt.figure(figsize=(20,5))
        plt.subplot(121)
        X, Y = np.meshgrid(self.t, self.w)
        plt.contourf(X,Y,self.D,levels=np.arange(self.ARange[0],self.ARange[1],0.05))
        plt.xlim(self.tRange[0],self.tRange[1])
        plt.vlines(0,self.wRange[0],self.wRange[1], color = 'k')
        plt.ylim(self.wRange[0],self.wRange[1])
        plt.ylabel('Wavelengths (nm)')
        plt.xlabel('Timedelays (ps)')

        plt.subplot(122)
        for i in np.arange(self.wRange[0],self.wRange[1],50):
            plt.plot(self.t,self.D[nearest(self.w,i),:])
        plt.xlim(self.tRange[0],self.tRange[1])
        plt.hlines((0),self.tRange[0],self.tRange[1], color = 'k')
        plt.vlines((0,self.neg_sub),self.ARange[0],self.ARange[1], color = 'k')
        plt.vlines((self.neg_sub),self.ARange[0],self.ARange[1], color = 'Blue')
        plt.ylim(self.ARange[0],self.ARange[1])
        plt.ylabel('\u0394A (mOD)')
        plt.xlabel('Timedelays (ps)')
        plt.show()
    
    def Chirp_UI(self):
        '''
        User interface for all the widgets used for data processing.
        '''
        #Widgets for cutting
        title1 = widgets.HTML(value = '<h1>TA Data Preprocessing</h1><br>'+
                             '<b>Set the wavelength range so that only clean data is left.</b><br>' +
                            '<b>Then set the Timedelay and Amplitude Range in a way that the Chirp correction is easy to see.</b>')
        size = '75%'
        wRange = widgets.IntRangeSlider(description = 'Wavelength Range',
                                        value = [self.w.min(),self.w.max()],
                                        min=self.w.min(), max=self.w.max(), step=5,
                                        style = {'description_width': 'initial'},
                                        layout=widgets.Layout(width=size))
        tRange = widgets.IntRangeSlider(description = 'Timedelay Range',
                                        value = [self.t.min(),5],
                                        min=self.t.min(), max=10, step=1,
                                        style = {'description_width': 'initial'},
                                        layout=widgets.Layout(width=size))
        ARange = widgets.FloatRangeSlider(description = 'Amplitude Range',
                                        value = [-0.85,1.01],
                                        min=-5, max=5, step=0.1,
                                        style = {'description_width': 'initial'},
                                        layout=widgets.Layout(width=size))
        neg_sub = widgets.FloatSlider(description = 'Subtract Negative from',
                                        value = -1,
                                        min=-3, max=3, step=0.1,
                                        style = {'description_width': 'initial'},
                                        layout=widgets.Layout(width=size))

        #Widgets for chirp correction
        title2 = widgets.HTML(value = '<b>Then choose the Chirp correction parameters</b>')
        y0 = widgets.FloatSlider(description = r'\(y_0\)',
                                        value = 1.07,
                                        min=-2, max=5, step=0.01,
                                        layout=widgets.Layout(width=size))
        A = widgets.FloatSlider(description = r'\(A\)',
                                        value = -0.423,
                                        min=-10, max=10, step=0.01,
                                        layout=widgets.Layout(width=size))
        tau = widgets.FloatSlider(description = r'\(\tau\)',
                                        value = 289.9,
                                        min=-1000, max=3000, step=1,
                                        layout=widgets.Layout(width=size))
        x0 = widgets.FloatSlider(description = r'\(x_0\)',
                                        value = 902,
                                        min=-1000, max=3000, step=1,
                                        layout=widgets.Layout(width=size))
        #Cutting
        Top_Box = widgets.VBox([wRange,tRange,ARange, neg_sub],layout=widgets.Layout(display='flex',align_items='flex-start'))
        #Plotting and interacting with the update function
        w = widgets.interactive_output(self.update,
                                       {'wRange' : wRange, 'tRange' : tRange, 'ARange' : ARange, 'neg_sub' : neg_sub,
                                       'y0' : y0, 'A' : A, 'tau' : tau, 'x0' : x0})
        #Chirp
        Bottom_Box = widgets.VBox([y0,A,tau,x0],layout=widgets.Layout(display='flex',align_items='flex-start'))

        w.layout.height = '100%'
        Top_Box.children[-1].layout.height = '100%'
        Bottom_Box.children[-1].layout.height = '100%'
        display(title1,Top_Box,w,title2,Bottom_Box)



class TA:
    '''
    Class to create TA data object. 
    '''
    def __init__(self, TA, time, wave):
        '''
        Upon initialization the ``svd_reconstruction_E15`` function is applied to the data to remove some noise and a Singular Value Decomposition is performed.

        :param TA: Takes in data matrix of TA data of size (time x wave) (without the timedelays and wavelengths).
        :param time: An array of timedelays.
        :param wave: An array of wavelengths. 

        :attributes TA Data: 
                    * self.TA
                    * self.time
                    * self.wave
        :attributes SVD Data:
                    * self.u
                    * self.s
                    * self.vh
        '''
        if time.shape[0] < wave.shape[0]:
            if TA.shape[0] == wave.shape[0]:
                self.TA   = svd_reconstruction_E15(TA,k_opt(TA))
            else:
                self.TA   = svd_reconstruction_E15(TA.T,k_opt(TA.T))
        else:
            self.TA = TA
        self.time = time
        self.wave = wave
        self.u, self.s, self.vh = np.linalg.svd(self.TA, full_matrices=False)
    
    def plot(self, times = None, norm = False, norm_at = None, norm_flip = False, title = None, ylim = None,  xlabel = 'Wavelength (nm)', ylabel = '\u0394A (mOD)'):
        '''
        Plots TA spectra at selected Timedelays. Options are given for choosing timedelays at which spectra are plotted, and if a normalization is to be done and where.

        :param times: A timedelays at which to plot spectra can be specified (in the form of a list), the ``nearest`` (found in ``functions``) function will be applied to the time delays if exact timedelay does no exist. Default ``[1500,1000,500,100,50,10,5,1,0.2]``.
        :param norm: Boolean, if True the spectra will be normalized at their maximum as long as ``norm_at=False``.
        :param norm_at: Specifies the wavelength at which the spectra will be normalized if ``norm = True``.
        :param norm_flip: Flips normalized spectra if normalization has left spectra in unwanted configuration.
        :param title: Adds a title to the plot.
        :param ylim: Specifies the y-axis (mOD) range over which the spectra are plotted.
        :param xlabel: Labels the x-axis with default :math:`Wavelength (nm)`.
        :param ylabel: Labels the y axis with default :math:`{\\Delta} A (mOD)`.
        '''
        if not times:
            times = np.asarray([1500,1000,500,100,50,10,5,1,0.2])
        color=plt.cm.rainbow(np.linspace(0,1,len(times)))
        if title:
            plt.title(title, fontsize=15)
        for t,c in zip(times,color):
            norm_factor = 1
            if norm:
                if norm_at:
                    norm_factor = 1/self.TA[nearest(self.wave, norm_at),nearest(self.time, t)]
                else:
                    norm_factor = 1/max(self.TA[:,nearest(self.time, t)])
                if norm_flip:
                        norm_factor = -norm_factor
            VIS_indx = np.where(self.wave < 800)[0]
            plt.plot(self.wave[VIS_indx],self.TA[VIS_indx,nearest(self.time, t)]*norm_factor, label = str(t) + ' ps',c=c)
            NIR_indx = np.where(self.wave > 800)[0]
            plt.plot(self.wave[NIR_indx],self.TA[NIR_indx,nearest(self.time, t)]*norm_factor,c=c)
        plt.hlines(0,min(self.wave),max(self.wave), lw=2)
        plt.xlim(min(self.wave),max(self.wave))
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend(loc="best",ncol = 2)
        if ylim:
            plt.ylim(ylim)
            
    def plotdyn(self, w, log = True, norm = False, scale = 1, label = None):
        '''
        Plots dynamics of TA spectra at a selected wavelength with options about scale and normalization.

        :param w: Wavelength at which dynamics are to be plotted (only one wavelength at a time). The ``nearest`` function will be applied if given wavelength does not exist.
        :param log: The dynamics will be plotted with the x-axis in log scale. Default is ``True``.
        :param norm:  Boolean, if True the dynamics will be normalized at their maximum.
        :param scale: Dynamics will be scaled (multiplied by) specified scale.
        :param label: Label can be specified (as a string).
        '''
        first_pos_time_indx = self.time[np.where(self.time > 0)[0][0]]
        if norm:
            if max(self.TA[nearest(self.wave,w),first_pos_time_indx:].T) > np.abs(min(self.TA[nearest(self.wave,w),first_pos_time_indx:].T)):
                dyn = self.TA[nearest(self.wave,w),:].T/max(self.TA[nearest(self.wave,w),first_pos_time_indx:].T)
            else:
                dyn = self.TA[nearest(self.wave,w),:].T/min(self.TA[nearest(self.wave,w),first_pos_time_indx:].T)
        else:
            dyn = self.TA[nearest(self.wave,w),:].T
        
        if label:
            plt.plot(self.time,dyn*scale, label = label)
        else:
            plt.plot(self.time,dyn*scale, label = str(w) + ' nm')
        if log:
            plt.xscale('log')
        if norm:
            plt.ylim(0,1.1)
        plt.xlim(first_pos_time_indx,max(self.time))
        plt.legend()
        plt.xlabel('Timedelays (ps)')
        plt.ylabel('\u0394A ')
        
    def plotsvd(self,num = 3, neg = False):
        '''
        Plots both the eigenvalues as well as a selected number of eigenvectors after an Singular Value Decomposition. The eigenvalues can give an idea of how many components are present in the TA data matrix
        and the eigenvectors can give an estimation of the shape of those components. These spectra are purely mathematical and not necessarily have a physical meaning in the TA spectra.

        :param num: Number of eigenvectors to print (represents spectra for TA). Default = 3.
        :param neg: If neg is true the eigenvectors are inverted (multiplied by -1).
        '''
        plt.subplot(121)
        plt.plot(self.s,'.')
        plt.subplot(122)
        self.svdguess = np.zeros((self.wave.shape[0],num))
        for i in range(num):
            if neg:
                plt.plot(self.wave,-self.u[:,i], label = 'SVD_' + str(i+1))
                self.svdguess[:,i] = -self.u[:,i]
            else:
                plt.plot(self.wave,self.u[:,i], label = 'SVD_' + str(i+1))
                self.svdguess[:,i] = -self.u[:,i]
        plt.hlines(0,min(self.wave),max(self.wave), lw=2)
        plt.xlim(min(self.wave),max(self.wave))
        plt.legend()
    
    def setGuess(self, MCR_guess):
        '''
        This function can initialise and store the spectral or concentration guess for input into the MCR analysis. 

        :param MCR_guess: Spectral or concentration guesses for MCR analysis in the form of a :math:`NxM` matrix with :math:`N` being number of components and :math:`M` being length of spectra. The length of spectra must match with self.wave.

        :attribute: self.MCR_guess
        '''
        self.MCR_guess = MCR_guess
    
    def setMCRRes(self, MCR_spec, MCR_dyn):
        '''
        This function initializes the results of the MCT analysis as attributes of the TA object. This step needs to be done before the ``plotMCR`` function can be called.

        :param MCR_spec: The spectral results of the MCR analysis, with the optimal spectra usually being used.
        :param MCR_dyn: The dynamics/concentration results of the MCR analysis, with the concentrations spectra usually being used.

        :attribute: * self.MCR_spec
                    * self.MCR_dyn
        '''
        self.MCR_spec  = MCR_spec
        self.MCR_dyn   = MCR_dyn
        
        
    def plotMCR(self, guess = False, norm = False):
        '''
        Plots the results of the MCR analysis with spectra and dynamics being plotted next to eachother with the option to just plot the initial guess for the MCR.

        :param guess: If ``True`` the guess spectra and not the MCR results are plotted.
        :param norm: If ``True`` the dynamics results are all normalized such that the sum of components are equal to 1 at the earliest times.

        '''
        if norm:
            init_total = 0
            for i in range(self.MCR_dyn.shape[1]):
                init_total += self.MCR_dyn[0,i]
            init_total = 1/init_total
        else:
            init_total = 1
        if guess:
            plt.suptitle('Initial Component Guess', fontsize=20,fontweight="bold")
            plt.plot(self.wave,self.MCR_guess)
            plt.hlines(0,self.wave.min(),self.wave.max(),lw =1)
            plt.xlim(self.wave.min(),self.wave.max())
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('\u0394A ')
        else:
            plt.figure(figsize=(20,5))
            plt.subplot(121)
            plt.title('Spectral Components', fontsize=15)
            plt.plot(self.wave,self.MCR_spec)
            plt.hlines(0,min(self.wave),max(self.wave), lw=2)
            plt.xlim(min(self.wave),max(self.wave))
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('\u0394A (norm.)')
            plt.subplot(122)
            plt.title('Component Dynmics', fontsize=15)
            plt.plot(self.time,self.MCR_dyn*init_total)
            plt.xscale('log')
            plt.ylim(0)
            plt.xlim(min(self.time),max(self.time))
            plt.xlabel('Timedelays (ps)')
            plt.ylabel('\u0394A (norm.)')

        


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        