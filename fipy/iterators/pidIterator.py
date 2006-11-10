## -*-Pyth-*-
 # ########################################################################
 # FiPy - a finite volume PDE solver in Python
 # 
 # FILE: "pidIterator.py"
 #                                     created: 10/31/06 {11:26:57 AM}
 #                                 last update: 11/9/06 {7:43:59 PM}
 # Author: Jonathan Guyer <guyer@nist.gov>
 # Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 # Author: James Warren   <jwarren@nist.gov>
 #   mail: NIST
 #    www: <http://www.ctcms.nist.gov/fipy/>
 #  
 # ========================================================================
 # This software was developed at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this software is not subject to copyright
 # protection and is in the public domain.  FiPy is an experimental
 # system.  NIST assumes no responsibility whatsoever for its use by
 # other parties, and makes no guarantees, expressed or implied, about
 # its quality, reliability, or any other characteristic.  We would
 # appreciate acknowledgement if the software is used.
 # 
 # This software can be redistributed and/or modified freely
 # provided that any derivative works bear some notice that they are 
 # derived from it, and any modified versions bear some notice that
 # they have been modified.
 # ========================================================================
 # 
 # History
 # 
 # modified   by  rev reason
 # ---------- --- --- -----------
 # 2006-10-30 JEG 1.0 original
 # 
 # ########################################################################
 ##

from fipy.iterators.iterator import Iterator

class PIDIterator(Iterator):
    """
    Adaptive iterator using a PID controller, based on::
        
        @article{PIDpaper,
           author =  {A. M. P. Valli and G. F. Carey and A. L. G. A. Coutinho},
           title =   {Control strategies for timestep selection in finite element
                      simulation of incompressible flows and coupled
                      reaction-convection-diffusion processes},
           journal = {Int. J. Numer. Meth. Fluids},
           volume =  47,
           year =    2005,
           pages =   {201-231},
        }
    """
    def __init__(self, dtMin, iterates=(), proportional=0.075, integral=0.175, derivative=0.01):
        Iterator.__init__(self, iterates=iterates)
        self.dtMin = dtMin
        self.dtPrev = dtMin
          
        self.proportional = proportional
        self.integral = integral
        self.derivative = derivative
        
        self.error = [1., 1., 1.]
        self.nrej = 0
        
    def _adjustTimestep(self, dt, dtMax):
        dt = max(dt, self.dtMin)
        dt = min(dt, dtMax)
        return dt
                        
    def _step(self, dtTry, dtMax, elapsed, sweepFn, failFn, *args, **kwargs):
        while 1:
            self.error[2] = sweepFn(iterates=self.iterates, dtTry=dtTry, *args, **kwargs)
            
            # omitting nsa > nsaMax check since it's unclear from 
            # the paper what it's supposed to do
            if self.error[2] > 1. and dtTry > self.dtMin:
                # reject the timestep
                failFn(iterates=self.iterates, dtTry=dtTry, *args, **kwargs)
                
                self.nrej += 1
                
                for var, eqn, bcs in self.iterates:
                    var.setValue(var.getOld())

                factor = min(1. / self.error[2], 0.8)
                
                dtTry = max(factor * dtTry, self.dtMin)
                
                self.dtPrev = dtTry**2 / self.dtPrev
            else:
                # step succeeded
                break
                
        dtNext = self.dtPrev * ((self.error[1] / self.error[2])**self.proportional 
                                * (1. / self.error[2])**self.integral 
                                * (self.error[1]**2 / (self.error[2] * self.error[0]))**self.derivative) 
              
        dtNext = self._adjustTimestep(dt=dtNext, dtMax=dtMax)
        
        self.dtPrev = dtNext
        
        self.error[0] = self.error[1]
        self.error[1] = self.error[2]
        
        return dtTry, dtNext
