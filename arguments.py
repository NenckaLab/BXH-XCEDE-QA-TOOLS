import argparse
import os
import shutil
from datetime import datetime
import subprocess
import glob
import yaml

class arguments(object):
    '''
    An instance of the default argument parser for the pipeline scheduler.
    Please use this instance in all pipelines for the scheduler to maintain consistent argument flags.
    Also, pass needs to be set up on the server using this, and have entries that match the passed -S flag.
    It's primarily a wrapper class, but standardizes some of the interactions.
    '''

    def __init__(self, args):
        '''
        Constructor
        By default, one should pass sys.argv to the args parameter when instantiating this object.
        '''
        self.args = args 
        self.results = []
        self.full_build_path = "/path/has/not/been/initialized" #"/some/arbitrary/path/that/does/not/exist/so/we/can/not/accidentally/delete/things"


    def parseArgs(self):
        parser = argparse.ArgumentParser(description='Default argument parser for all pipeline scheduler pipelines.')
        
        #server related flags
        parser.add_argument('-S', '--Server', help='The server identifier.', default="CIRXNAT2")
        parser.add_argument('-A', '--Address', help='The server url.', default='http://cirxnat2.rcc.mcw.edu/xnat')
        
        #path related flags
        parser.add_argument('-ps', '--pipeline_scheduler', help='The path to the local pipeline scheduler and, ultimately, the pipelines.', default='/localdata/scheduler')
        parser.add_argument('-bd', '--build_directory', help='The path in which to build/run this pipeline.', default='/localdata/scheduler/build')
        
        #Which experiment to pull
        parser.add_argument('-P', '--project', help='XNAT project.', required=True)
        parser.add_argument('-s', '--subject', help='XNAT Subject.',required=True)
        parser.add_argument('-e', '--experiment', help='XNAT Experiment.', required=True)
#         parser.add_argument('-sd', '--scan-description', help='Required scan description.', action='append', default = [])
#         parser.add_argument('-rd', '--reconstruction-description', help='Required reconstruction description.', action='append', default = [])
        parser.add_argument('-pl', '--pipeline', help='Configuration pipeline to run, used to recover yaml config', required=True)
        
        #outputs
        parser.add_argument('-rf', '--results_folder_name', help='The reconstruction folder name to load the results into.', required=True)
        
        #pipeline special features
        parser.add_argument('-v', '--verbose', help='Verbose output.', action="store_true")
        parser.add_argument('-sf', '--subfolder', help='Subfolder with any special processing parameters/subsets.', default='./')
        self.results = parser.parse_args()
        
        x=datetime.now()
        y=x.strftime("%Y%m%d_%H%M%S_%f")
        self.full_build_path=os.path.join(self.results.build_directory,y)
        if(not os.path.isdir(self.full_build_path)):
            os.makedirs(self.full_build_path)
            
            
        #get the appropriate yaml configuration
        schedules=[]
        for x in glob.glob('{}/pipelines/schedules/*.yaml'.format(self.results.pipeline_scheduler)):
            #print(x)
            with open(x) as f:
        
                data = yaml.load(f, Loader=yaml.FullLoader)
                #print(data)
                if("example" not in x):
                    schedules.append(data)
        self.yamlConfig = self.findmatch(schedules)
                
        return
    
    def findmatch(self, sched):
        for x in sched:
            if(self.results.project == x['project']):
                for p in x['pipelines']:
                    if(self.results.pipeline == p['name']):
                        return p
        return "FAILED TO FIND MATCH"
    
    def getPipelinePath(self):
        '''Returns the pipeline path.'''
        return os.path.join(self.results.pipeline_scheduler,"pipelines/sources")
    
    def getBuildPath(self):
        '''Returns the build path.'''
        #should it create the directory here? Then it's done and handled.
        #also, a unique name, timestamp at parseargs?
        return self.full_build_path
    
    
    def cleanup(self):
        ''' Far from foolproof. Requires a minimum level of depth. Use with caution. '''
        #some sort of check here
        #I think we may want to check a few things, 
        #first, that the path isn't empty, or root, or anything like that
        #second, I'd like some sort of succeed/fail flag, so, we can retain on failure, but delete on success
        safety=0
        x=self.full_build_path
        while(os.path.split(x)[1] != ''):
            x=os.path.split(x)[0]
            safety += 1
        if(safety >= 3):
            shutil.rmtree(self.full_build_path)
    
    def getProject(self):
        return self.results.project
    def getSubject(self):
        return self.results.subject
    def getExperiment(self):
        return self.results.experiment
    def getResultsFolderName(self):
        return self.results.results_folder_name 
    def getVerbose(self):
        return self.results.verbose
    def getSubfolder(self):
        return self.results.subfolder 
    
    def getConfig(self):
        return self.yamlConfig
    
    def getEverything(self):
        return self.results
        
    
    #*********************** these four functions are the interface for pass *************************

    def getUser(self):
        #'Does something'
        return (subprocess.check_output("pass /{}/user".format(self.results.Server.lower()), shell=True)).replace(b'\n',b'').decode("utf-8") #self.user

    def getPassword(self):
        return (subprocess.check_output('pass /{}/pass'.format(self.results.Server.lower()), shell=True)).replace(b'\n',b'').decode("utf-8")
    
    def getAddress(self):
        return self.results.Address
    

