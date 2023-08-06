import numpy as np
import matplotlib.pyplot as plt

from femtomat.functions import nearest, svd_reconstruction_E15, rmse_special, k_opt

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
        if norm:
            dyn = self.TA[nearest(self.wave,w),:].T/max(np.abs(self.TA[nearest(self.wave,w),:].T))
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
        plt.xlim(min(self.time),max(self.time))
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

        


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        