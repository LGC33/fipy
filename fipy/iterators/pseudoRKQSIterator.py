## -*-Pyth-*-
 # ########################################################################
 # FiPy - a finite volume PDE solver in Python
 # 
 # FILE: "pseudoRKQSIterator.py"
 #                                     created: 10/31/06 {11:26:57 AM}
 #                                 last update: 11/9/06 {7:43:49 PM}
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

class PseudoRKQSIterator(Iterator):
    """
    Adaptive iterator based on the ``rkqs`` (Runge-Kutta
    "quality-controlled" stepper) algorithm of Numerical Recipes in C: 2nd
    Edition, Section 16.2.
    
    Not really appropriate, since we're not doing Runge-Kutta steps
    in the first place, but works OK.
    """
    def __init__(self, iterates=(), safety=0.9, pgrow=-0.2, pshrink=-0.25, errcon=1.89e-4):
        Iterator.__init__(self, iterates=iterates)
        self.safety = safety
        self.pgrow = pgrow
        self.pshrink = pshrink
        self.errcon = errcon
        
    def _step(self, dtTry, dtMax, elapsed, sweepFn, failFn, *args, **kwargs):
        residual = 1e100
        while residual > 1.:
            residual = sweepFn(iterates=self.iterates, dtTry=dtTry, *args, **kwargs)
            
            if residual > 1.:
                # step failed
                failFn(iterates=self.iterates, dtTry=dtTry, *args, **kwargs)
                    
                # revert
                for var, eqn, bcs in self.iterates:
                    var.setValue(var.getOld())
                    
                    dtTry = max(self.safety * dtTry * residual**self.pgrow, 0.1 * dtTry)
                if elapsed + dtTry == elapsed:
                    raise "step size underflow"

        if residual > self.errcon:
            dtNext = dtTry * self.safety * residual**self.pshrink
        else:
            dtNext = 5 * dtTry
            
        return dtTry, dtNext
