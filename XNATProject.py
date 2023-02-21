'''
Created on Sep 29, 2016

@author: bradswearingen
@version: 1.1
'''

#v1.1 Add a few JSON returns. Switch from keepalive to cookies. 1/25/17 BS
#need to decide which is the master copy. Probably the version in ReconstructionNameCorrection
    
import subprocess
import json
import time

class XNATProject(object):
    '''
    An instance of XNAT.
    '''
    
    #constants
    DB_SCAN_ROW_ID = 0
    DB_SCAN_ID = 1
    DB_SCAN_TYPE = 2
    DB_SCAN_QUALITY = 3
    DB_SCAN_XSITYPE = 4
    DB_SCAN_NOTE = 5
    DB_SCAN_SERIES = 6
    DB_SCAN_URI = 7

    def __init__(self, address, project, user, password):
        '''
        Constructor
        '''
        self.address = address
        self.project = project
        self.user = user
        self.password = password
        self.cookie = address.replace('/', '_').replace(':','_') 

    #PRIVATE FUNCTIONS
    def __processResultsToSeeIfServerIsReady(self, results):
        if('Unable to find the specified experiment.' in results):
                #the project hasn't been created yet
                print("Project not yet created.")
                return False
        else:
            #see if the autorun pipe is done
            parsed_json = json.loads(results)
            print("Parsing results.")
            if(parsed_json['events'] == []):
                print("Events currently empty. Import in process.")
                return False
            for element in parsed_json['events']:
                if(element['event_status'] == 'Running'):
                    #try again later if anything is currently running
                    print("Something is still running.")
                    return False
                elif(element['event_action'] == 'AutoRun'):
                    if((element['event_status'] == 'Complete') or (element['event_status'] == 'Failed')):
                        #go ahead and move to the next step if the Autorun is finished
                        print("AutoRun is complete.")
                        return True
                    else:
                        print("AutoRun has not completed.")
                        return False
                else:
                    pass
        print("Defaulting to wait.")
        return False
    
    def __destExpSetupClean(self, myExperimentName): 
        #check if there are results
#         curlCmd = "curl -k --keepalive-time 5 -s -X GET -u " + curlStuff[USER] + ":" + curlStuff[PWD] + " " + \
#             '"' + curlStuff[ADDR] + "/data/archive/projects/" + curlStuff[PROJ] + '/experiments/' + myExperimentName + '/history?format=json"'
        curlCmd = ('%s/experiments/%s/history?format=json"' % (self.getCurlGetBaseNoSubject(), myExperimentName))
        print (curlCmd)
        #retrieve from source xnat
        result = subprocess.check_output(curlCmd, shell=True)
        print (result)
        readyForPipeline = self.__processResultsToSeeIfServerIsReady(result)
        return readyForPipeline
    
    def __waitForExp(self, myExperimentName, maxWait, delay=60):
        #polls and waits for experiment to complete loading, returns True if exp exists, False if not.
        startTime = time.time()
        now = time.time()
        #see if the item has been created yet
        while(maxWait > (now - startTime)):
            print("start:%d \ncurrent:%d \nelapsed:%d \nmax:%d \n\n" % (startTime, now, (now-startTime), maxWait))
            if(not self.__destExpSetupClean(myExperimentName)):
                print("Server wasn't ready.")
                time.sleep(delay)
                now = time.time()
            else:
                #the new experiment exists
                return True
        #Time expired
        print("System timed out while waiting for %s to be created." % myExperimentName)
        return False
      
    #SETTERS/GETTERS
    def setUser(self, user):
        self.user = user
        
    def setPassword(self, password):
        self.password = password 
        
    def setProject(self, project):
        self.project = project 
       
    def setAddress(self, address):
        self.address = address
        
    def getUser(self):
        return self.user
    
    def getProject(self):
        return self.project
    
    def removeDoubles(self, curlCmd):
        return curlCmd.replace('//data', '/data')
    
    def getCurlGetBase(self):
        curlBase = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X GET -u " + self.user + ":" + self.password + " " + \
            '"' + self.address + "/data/archive/projects/" + self.project + "/subjects"
        return self.removeDoubles(curlBase)
    
    def getCurlGetBaseNoSubject(self):
        curlBase = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X GET -u " + self.user + ":" + self.password + " " + \
            '"' + self.address + "/data/archive/projects/" + self.project
        return curlBase
    
    def getCurlPutBase(self):
        curlBase = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X PUT -u " + self.user + ":" + self.password + " " + \
            '"' + self.address + "/data/archive/projects/" + self.project + "/subjects"
        return self.removeDoubles(curlBase)
    
    def getCurlPostBase(self):
        curlBase = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X POST -u " + self.user + ":" + self.password + " " + \
            '"' + self.address + "/data/archive/projects/" + self.project + "/subjects"
        return self.removeDoubles(curlBase)
    def getCurlPostBaseNoSubject(self):
        curlBase = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X POST -u " + self.user + ":" + self.password + " " + \
            '"' + self.address + "/data/archive/projects/" + self.project
        return self.removeDoubles(curlBase)
    
    def getCurlDeleteBase(self):
        curlBase = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X DELETE -u " + self.user + ":" + self.password + " " + \
            '"' + self.address + "/data/archive/projects/" + self.project + "/subjects"
        return self.removeDoubles(curlBase)
    
    def getCookies(self):
        return "-c " + self.cookie + " -b " + self.cookie
    def getUserPassword(self):
        return "-u " + self.user + ":" + self.password
    def getAddress(self):
        return self.address 
    
    def curlStringReplace(self, myString):
        #prepares a string for sending as part of a curl uri
        newString = myString.lstrip()
        newString = newString.rstrip()
        newString = newString.replace(' ', '+')
        newString = newString.replace('&apos;', '%27')
        newString = newString.replace('&quot;', '%22')
        newString = newString.replace('\n', '%0A')
        newString = newString.replace('\r', '%0D')
        newString = newString.replace('-', '%2D')
        return newString
    
    #RETRIEVAL ITEMS
    def getSubjects(self):
        #returns a csv copy of the list of subjects
        curlCmd = self.getCurlGetBase() + '?format=csv"'
        curlCmd = self.removeDoubles(curlCmd)
        curlOutput = subprocess.check_output(curlCmd, shell=True)
        return curlOutput
    
    def getSubjectsJSON(self):
        #Get the subject list and split it up into individual subjects
        curlCmd = '%s?format=json"' % (self.getCurlGetBase())
        curlCmd = self.removeDoubles(curlCmd)
        #print curlCmd
        curlOutput = subprocess.check_output(curlCmd, shell=True)
        print (curlOutput)
        subjects = (json.loads(curlOutput))['ResultSet']['Result']
        return subjects
    
    def getExperiments(self, subjectName):
        #query the scans from the old database using the old subject name
        curlCmd = self.getCurlGetBase() + "/" + subjectName + '/experiments?format=csv"'
        curlCmd = self.removeDoubles(curlCmd)
        curlOutput = subprocess.check_output(curlCmd, shell=True)
        return curlOutput
    
    def getExperimentsJSON(self, subjectName):
        #get the experiments and split them up
        curlCmd = '%s/%s/experiments?format=json"' % (self.getCurlGetBase(), subjectName)
        curlCmd = self.removeDoubles(curlCmd)
        curlOutput = subprocess.check_output(curlCmd, shell=True)
        experiments = (json.loads(curlOutput))['ResultSet']['Result']
        #experiments = [{"date":"2014-10-28","xsiType":"xnat:mrSessionData","xnat:subjectassessordata/id":"XNAT_E00130","insert_date":"2016-07-20 13:07:19.808","project":"UWARC","ID":"XNAT_E00130","label":"4_ASN_test_3D_TOF_28_10_2014_1","URI":"/data/experiments/XNAT_E00130"}, ...]
        return experiments
    
    def getExperimentDateJSON(self, subjectName, experiment):
        #get the experiments and split them up
        curlCmd = '%s/%s/experiments?format=json"' % (self.getCurlGetBase(), subjectName)
        curlCmd = self.removeDoubles(curlCmd)
        #print curlCmd
        curlOutput = subprocess.check_output(curlCmd, shell=True)
        #print curlOutput
        experiments = (json.loads(curlOutput))['ResultSet']['Result']
        for x in experiments:
            if(x['label'] == experiment):
                return x['date']
        return None
        
    def zipScansToFile(self, subjectName, experimentId, myFile, scanlist = 'ALL'):
        #returns a zip file with all of the resource files
        curlCmd = "curl -k -c " + self.cookie + " -b " + self.cookie + " -X GET -o " + myFile + " -u " + self.user + ":" + self.password + " -s" + \
            ' "' + self.address + "/data/archive/projects/" + self.project + "/subjects/" + \
            subjectName + "/experiments/" + experimentId + '/scans/' + scanlist +'/files?format=zip" -w "Found"'
        curlCmd = self.removeDoubles(curlCmd)
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        return curlOutput
    
    def legacyScansToFile(self, subjectName, experimentId, myFile, scanlist = 'ALL'):
        #returns a zip file with all of the resource files
        curlCmd = "curl -k -c " + self.cookie + " -b " + self.cookie + " -X GET -o " + myFile + " -u " + self.user + ":" + self.password + " -s" + \
            ' "' + self.address + "/data/archive/projects/" + self.project + "/subjects/" + \
            subjectName + "/experiments/" + experimentId + '/scans/' + scanlist +'/files?format=zip&structure=legacy" -w "Found"'
        curlCmd = self.removeDoubles(curlCmd)
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        return curlOutput
        
    def zipResourcesToFile(self, subjectName, experimentId, myFile, resourceId):
        #returns a zip file with all of the scan files
        curlCmd = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X GET -o " + myFile + " -u " + self.user + ":" + self.password + \
            ' "' + self.address + "/data/archive/projects/" + self.project + "/subjects/" + \
            subjectName + "/experiments/" + experimentId + '/resources/' + resourceId + '/files?format=zip"'
        #print curlCmd
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        return curlOutput
        
    def zipResourceToFile(self, subjectName, experimentId, myLocalPath, resourceId, myFile):
        #returns a specified file - note that this has truncated from other versions. zipResourcesToFile is closer to the original
        curlCmd = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X GET -o " + myLocalPath + " -u " + self.user + ":" + self.password + \
            ' "' + self.address + "/data/archive/projects/" + self.project + "/subjects/" + \
            subjectName + "/experiments/" + experimentId + '/resources/' + resourceId + '/files/' + myFile + '"'
        #print curlCmd
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        return curlOutput
    
    def getResourceListJSON(self, subjectName, experimentId):
        curlCmd = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X GET -u " + self.user + ":" + self.password + \
            ' "' + self.address + "/data/archive/projects/" + self.project + "/subjects/" + \
            subjectName + "/experiments/" + experimentId + '/resources/"'
        #print curlCmd
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        #print curlOutput
        parsed_json = json.loads(curlOutput)
        return parsed_json
    
    def getResourceFilesJSON(self, subjectName, experimentId, resourceId):
        curlCmd = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X GET -u " + self.user + ":" + self.password + \
            ' "' + self.address + "/data/archive/projects/" + self.project + "/subjects/" + \
            subjectName + "/experiments/" + experimentId + '/resources/' + resourceId + '/files"'
        #print curlCmd
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        parsed_json = json.loads(curlOutput)
        return parsed_json
    
    def getReconstructionListJSON(self, subjectName, experimentName):
        #returns a library of the reconstructions
        curlCmd = self.getCurlGetBase() + "/" + subjectName + '/experiments/' + experimentName + '/reconstructions?format=json"'
        #print curlCmd
        result = subprocess.check_output(curlCmd, shell=True)
        #print result
        parsed_json = json.loads(result)
        #print(parsed_json)
        return parsed_json
    
    def getReconstructionQty(self, subjectName, experimentName):
        #return the number of reconstructions
#         curlCmd = self.getCurlGetBase() + "/" + subjectName + '/experiments/' + experimentName + '/reconstructions?format=json"' 
#         result = subprocess.check_output(curlCmd, shell=True)
#         #print result
#         parsed_json = json.loads(result)
#         print(parsed_json)
#         #print (parsed_json['ResultSet'])
#         #print (parsed_json['ResultSet']['totalRecords'])
        parsed_json = self.getReconstructionListJSON(subjectName,experimentName)
        return int(parsed_json['ResultSet']['totalRecords'])
    
    def getReconstructionFolderNames(self, subjectName, experimentName):
        #returns a list of all reconstructions folders in an experiment
        folderNames = []
        
        parsed_json = self.getReconstructionListJSON(subjectName,experimentName)
        for result in parsed_json['ResultSet']['Result']:
            folderNames.append(result['ID'])
        
        return folderNames
    
    def getReconstructionFilenames(self, subjectName, experimentName, reconstructionFolderName):
        #returns the names of all files within a reconstruction folder
        fileNames = []
        curlCmd = self.getCurlGetBase() + "/" + subjectName + '/experiments/' + experimentName + '/reconstructions/' + reconstructionFolderName + '/files?format=json"'
        curlCmd = self.removeDoubles(curlCmd)
        result = subprocess.check_output(curlCmd, shell=True)
        #print result
        parsed_json = json.loads(result)
        #print(parsed_json)
        for result in parsed_json['ResultSet']['Result']:
            fileNames.append(result['Name'])
        return fileNames
    
    def zipReconstructionToFile(self, subjectName, experimentId, reconstructionFolderName, myFile):
        #returns a zip file with all of the scan files
        curlCmd = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X GET -o " + myFile + " -u " + self.user + ":" + self.password + \
            ' "' + self.address + "/data/archive/projects/" + self.project + "/subjects/" + \
            subjectName + "/experiments/" + experimentId + '/reconstructions/' + reconstructionFolderName + '/files?format=zip"'
        curlCmd = self.removeDoubles(curlCmd)
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        return curlOutput
    
    def zipReconstructionsToFile(self, subjectName, experimentId, myFile):
        #returns a zip file with all of the scan files
        curlCmd = "curl -k -c " + self.cookie + " -b " + self.cookie + " -s -X GET -o " + myFile + " -u " + self.user + ":" + self.password + \
            ' "' + self.address + "/data/archive/projects/" + self.project + "/subjects/" + \
            subjectName + "/experiments/" + experimentId + '/reconstructions/ALL/files?format=zip"'
        curlCmd = self.removeDoubles(curlCmd)
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        return curlOutput

    def getScans(self, subjectName, experimentId):
        curlCmd = self.getCurlGetBase() + "/" + subjectName + "/experiments/" + experimentId + "/scans?format=csv"
        curlCmd = self.removeDoubles(curlCmd)
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        return curlOutput
    
    def getScansJSON(self, subjectName, experimentId):
        #returns a list of scan dictionaries
        curlCmd = self.getCurlGetBase() + "/" + subjectName + "/experiments/" + experimentId + '/scans?format=json"'
        curlCmd = self.removeDoubles(curlCmd)
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        scansFull = (json.loads(curlOutput))['ResultSet']['Result']
        return scansFull

    def getScansList(self, subjectName, experimentId):
        #curlCmd = self.getCurlGetBase() + "/" + subjectName + "/experiments/" + experimentId + '/scans?format=json"'
        #curlOutput = subprocess.check_output(curlCmd,shell=True)
        scansFull = self.getScansJSON(subjectName, experimentId)
        scansList = []
        for a in scansFull:
            scansList.append(a['ID'])
        return scansList

    def getScansDescriptions(self, subjectName, experimentId):
        curlCmd = self.getCurlGetBase() + "/" + subjectName + "/experiments/" + experimentId + '/scans?format=json"'
        curlOutput = subprocess.check_output(curlCmd,shell=True)
        scansFull = (json.loads(curlOutput))['ResultSet']['Result']
        scansList = []
        for a in scansFull:
            scansList.append(a['series_description'])
        return scansList
                
    def getSubjectDataXML(self, subjectName):
        #get the XML structure of the subject
        #this should be updated to actually return the file, instead of redirecting it to an output file and returning the name
        curlCmd = self.getCurlGetBase() + '/' + subjectName + '/scans?format=xml" > xmlFile.xml'
        #retrieve from source xnat
        subprocess.check_output(curlCmd, shell=True)
        return 'xmlFile.xml'

    def getPipelineHistoryJSON(self, subjectName, experimentName):
        #get the pipeline history JSON structure of the scan session
        curlCmd = self.getCurlGetBase() + "/" + subjectName + '/experiments/' + experimentName + '/history"'
        #retrieve from source xnat
        result = subprocess.check_output(curlCmd, shell=True)
        return result

    def schedulePipeline(self, pipeline, exp):
        curlCmd = self.getCurlPostBaseNoSubject() + '/pipelines/' + pipeline + '/experiments/' + exp + '?match=LIKE"'
        print (curlCmd)
        subprocess.check_output(curlCmd, shell=True)
        return 

    def deleteRecon(self, subj, exp, recon):
        #delete the incorrect file & folder
        #server.zipReconstructionToFile(subjectLine[DB_SUBJECT_NAME], experimentLine[DB_EXP_LABEL], recon, os.path.join(args.OutputDirectory, "tmp.zip"))
        curlcmd = self.getCurlDeleteBase() + '/' + subj + '/experiments/' + exp + '/reconstructions/' + recon + '"' 
        subprocess.check_output(curlcmd, shell=True)
        #                curl -u admin:b=58To:CjS -X DELETE "http://cirxnat1.rcc.mcw.edu/xnat/data/archive/projects/Sandbox/subjects/4_WISC_IH_1535/experiments/4_WISC_IH_1535_22_06_2016_4_2/reconstructions/4_WISC_IH_1535_22_06_2016_4_2_6001"
        return 

    def printAllExperiments(self):
        #returns a dictionary of all {exp, subj} on this server/project. Note python server instance contains one project!
        experimentList = []
        #Get the subject list and split it up into individual subjects
        subjects = self.getSubjectsJSON()
        for subject in subjects:
            #print subject['ID']
            experiments = self.getExperimentsJSON(subject['ID'])
            for exp in experiments:
                expDict = {'exp':exp['label'], 'subj': subject['ID']}
                experimentList.append(expDict)
                #print "%s" % (exp['label'])
        return experimentList
    
    def createScans2(self, subject, mfile, sleepTime = 240):
        #Load the imported scans into the destination XNAT archive
        #this one only works if it is an existing project
        curlCmd = "curl -k -c %s -b %s -s -X POST -u %s:%s --data-binary @%s -H 'Content-Type: application/zip' " + \
            "%s/data/services/import?project=%s&subject=%s&overwrite=append&inbody=true'" % ( self.cookie, self.cookie, self.user, self.password, mfile, self.address, self.project, subject)   #'&session=' + myInputExperiment + 
        curlCmd = self.removeDoubles(curlCmd)
        print ("   %s" % curlCmd)
        curlOutput = subprocess.check_output(curlCmd, shell=True)    
        #fireOutput('Prearchive Experiment: ', curlCmd)
        print ("        Sleeping")
        #give new server 4 minutes to perform the autorun sequence
        time.sleep(sleepTime)
        return curlOutput
    
    def addScans(self, subject, experiment, mfile, sleepTime = 240, test = False):
        #Load the imported scans into the destination XNAT archive
        #this one only works if it is an existing project
        curlCmd = "curl -k -c %s -b %s -s -X POST -u %s:%s --data-binary @%s -H 'Content-Type: application/zip' '%s/data/services/import?project=%s&subject=%s&session=%s&overwrite=append&inbody=true'" % ( self.cookie, self.cookie, self.user, self.password, mfile, self.address, self.project, subject, experiment )   
            #'&session=' + myInputExperiment + 
#         curlCmd = "curl -c %s -b %s -s -X POST -u %s:%s --data-binary @%s -H 'Content-Type: application/zip' " % ( self.cookie, self.cookie, self.user, self.password, mfile)
        curlCmd = self.removeDoubles(curlCmd)
        print("   %s" % curlCmd)
        if(not test):
            curlOutput = subprocess.check_output(curlCmd, shell=True)
        print("        Sleeping")
        #give new server 4 minutes to perform the autorun sequence
        time.sleep(sleepTime)
        return curlOutput
    
    def getDicomHeader(self, experiment, scanNum):
        curlCmd = "curl -c %s -b %s -s -X GET -u %s:%s %s/REST/services/dicomdump?src=/archive/projects/%s/experiments/%s/scans/%s" % (self.cookie, self.cookie, self.user, self.password, self.address, self.project, experiment, scanNum)
        curlCmd = self.removeDoubles(curlCmd)
        #print "    %s" % curlCmd
        curlOutput = subprocess.check_output(curlCmd, shell=True)
        #print curlOutput
        return (json.loads(curlOutput))['ResultSet']['Result']
    
    def getDicomTag(self, subject, experiment, tagID):
        #pass in the tag id as a 8 digit string, or a valid text string, to get back the value
        
        #examples
        #curl -u ${user} ${xnat_url}/data/services/dicomdump?src=/archive/projects/${project}/subjects/${subject}/experiments/${session}
        #curl -u ${user} ${xnat_url}/data/services/dicomdump?src=/archive/projects/${project}/subjects/${subject}/experiments/${session}/scans/${scan}
        #curl -u ${user} "${xnat_url}/data/services/dicomdump?src=/archive/projects/${project}/subjects/${subject}/experiments/${session}&field=0020000d"
        #curl -u ${user} "${xnat_url}/data/services/dicomdump?src=/archive/projects/${project}/subjects/${subject}/experiments/${session}&field=PatientID&field=PatientName"
        #curl -u ${user} "${xnat_url}/data/services/dicomdump?src=/archive/projects/${project}/subjects/${subject}/experiments/${session}&field=00291020&format=xml"
        if(tagID.isdigit()):
            tagID = tagID + 'd'
        curlCmd = 'curl -k -c {} -b {} -s -u {}:{} "{}/data/services/dicomcump?src=/archive/projects/{}/subjects/{}/experiments/{}&field={}'.format(self.cookie, self.cookie, self.user, self.password, self.address, self.project, subject, experiment, tagID)
        print(curlCmd)
        curlOutput = subprocess.check_output(curlCmd, shell=True)
        print(curlOutput)
        return
        
        

