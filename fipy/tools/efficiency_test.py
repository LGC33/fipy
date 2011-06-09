from distutils.core import Command
import os
import string
import sys
import glob
import ez_setup
from setuptools.command.test import test as _test

class Efficiency_test(Command):
    description = "run FiPy efficiency tests"

    user_options = [ ('minimumelements=', None, 'minimum number of elements'),
                     ('factor=', None, 'factor by which the number of elements is increased'),
                     ('inline', None, 'turn on inlining for the efficiency tests'),
                     ('cache', None, 'turn on variable caching'),
                     ('maximumelements=', None, 'maximum number of elements'),
                     ('sampleTime=', None, 'sampling interval for memory high-water'),
                     ('path=', None, 'directory to place output results in'),
                     ('uploadToCodespeed', None, 'flag to upload data to Codespeed')]
    
    def initialize_options(self):
        self.factor = 10
        self.inline = 0
        self.cache = 0
        self.maximumelements = 10000
        self.minimumelements = 100
        self.sampleTime = 1
        self.path = None
        self.cases = ['examples/cahnHilliard/mesh2D.py']
        self.uploadToCodespeed = False
    
    def finalize_options(self):
        self.factor = int(self.factor)
        self.maximumelements = int(self.maximumelements)
        self.minimumelements = int(self.minimumelements)
        self.sampleTime = float(self.sampleTime)

    def run(self):
        import time
        import os

        for case in self.cases:
            print "case: %s" % case
            
            if self.path is None:
                testPath = os.path.split(case)[0]
            else:
                testPath = self.path
                
            if not os.access(testPath, os.F_OK):
                os.makedirs(testPath)
            
            testPath = os.path.join(testPath, '%s.dat' % os.path.split(case)[1])
            
            if not os.path.isfile(testPath):
                f = open(testPath, 'w')

                f.write("\t".join(["--inline".center(10), "--cache".center(10), "Date".center(25),\
                        "Elements".center(10), "total runtime(s)".rjust(15)]))
                f.write("\n")
                f.flush()
            else:
                f = open(testPath, 'a')
            
            numberOfElements = self.minimumelements

            while numberOfElements <= self.maximumelements:
                print "\tnumberOfElements: %i" % numberOfElements
                
                cmd = ["python", "-W ignore", case, '--numberOfElements=%i' % numberOfElements, '--no-display nodisp']
                
#                if self.inline:
#                    cmd += ['--inline']
                    
#                if self.cache:
#                    cmd += ['--cache']
#                else:
#                    cmd += ['--no-cache']

                output = "\t".join([str(self.inline).center(10), str(self.cache).center(10),\
                                   (time.ctime()).center(25), str(numberOfElements).center(10)])
                
                timeCmd = cmd + ['--measureTime runtime']
                w, r = os.popen2(' '.join(timeCmd))
##                print "' '.join(timeCmd): ", ' '.join(timeCmd)
##                raw_input()
                outputlines = r.readlines()
                outputlist=outputlines[0].split()
                runtime = [outputlist[outputlist.index("runtime:")+1]]
                print runtime
                output += '\t' + ''.join(runtime).strip()
                r.close()
                w.close()

#                memCmd = cmd + ['--measureMemory', '--sampleTime=%f' % self.sampleTime]

#                w, r = os.popen4(' '.join(memCmd))
#                output += '\t' + ''.join(r.readlines()).strip()
                r.close()
                w.close()
                if numberOfElements == self.maximumelements:    
                    f.write(output + '\n' + "-"*100 + '\n')
                    f.flush()
                else:
                    f.write(output + '\n')
                    f.flush()
                numberOfElements *= self.factor
                if self.uploadToCodespeed:
                    from fipy.tools import save_efficiency_test_result
                    
#                    print "Hello, world"
#                    import urllib, urllib2
                    import time 
                    import pysvn 

                    revnum = pysvn.Client().info('.')['revision'].number
                    revdate =  time.ctime(pysvn.Client().info('.')['commit_time'])
                    from datetime import datetime
                    data = {
#                        'commitid': revnum,
                        'commitid': '60',
                        'branch': 'default',
#                        'branch' : 'efficiency_test'
#                        'project': 'FiPy',
                        'project': 'Prototype Test',
#                        'revision_date': revdate,
#                        'executable': 'setup.py efficiency_test',
                        'executable': 'datatest.py',
                        'benchmark': 'float',
                        'environment': "Test",
#                        'result_value': runtime[0],
                        'result_value': 1.0,
                        'result_date': datetime.today(),
##                        'result_date': time.ctime(),
                        }
                       
                    save_efficiency_test_result.add(data)
                   
            f.close()
            
