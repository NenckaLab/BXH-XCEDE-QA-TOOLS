import glob
from datetime import date, timedelta

from XNATProject import XNATProject
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import sys

# get the relative path to our bin so we can include these items.
sys.path.insert(0, '../../../bin')
import arguments
import XNATProject
import os

# Pipeline scheduling pathnames
finalOutput = '/localdata/scheduler/output/'

# Location to save output after pipeline has run
# USED LINE 98 FOR SCP
SERVER_OUTPUT = ''

# Variables that are updated by scan
exp_date = date.today()
delta = timedelta(1)
subject = ""
coil = ''
scanner = ''


def main():

    # some preliminary items I expect will be the same for every pipeline
    myparser = arguments.arguments(sys.argv)
    myparser.parseArgs()
    source = XNATProject.XNATProject(myparser.getAddress(), myparser.getProject(), myparser.getUser(),
                                     myparser.getPassword())
    prefix = "{}_{}_{}_".format(myparser.getProject(), myparser.getSubject(), myparser.getExperiment())
    y = myparser.getBuildPath()
    logfile = os.path.join(y, "log.txt")
    logwriter = open(logfile, 'w')
    logwriter.write("prefix: {}\n".format(prefix))
    x = myparser.getEverything()

    logwriter.write("{}".format(x))
    logwriter.write("Some data \n")
    logwriter.write("Let's see, what else, need to upload this file at the end as well, should there be a wrapper?")

    x = myparser.getConfig()
    logwriter.write("\n\nClient side retrieval of YAML for this pipeline:\n")
    logwriter.write("{}".format(x))

    # download the scans
    alldescs = []
    for c in x['requiredScans']:
        for z in c['token']:
            alldescs.append(z)
    print(y)
    source.zipScansToFile(myparser.getSubject(), myparser.getExperiment(), os.path.join(y, "tmp.zip"))
    with ZipFile(os.path.join(y, "tmp.zip"), 'r') as zipObj:
        zipObj.extractall(y)

# Folder that contains the QA scans
    for element in glob.glob('{}/{}/scans/*-FATES_EPI_RUN/resources/DICOM/files/'.format(myparser.getBuildPath(), myparser.getExperiment())):
        if os.path.isdir(element):
            files = os.listdir(element)
            for f in files:
                os.renames(element + f, y + '/input/fmri_input/' + f)
    runSingularity(y)
    unzipOutput(y)
    renameOutput(y)
    myparser.cleanup()

# Takes input and run the QA Singularity container
def runSingularity(y):
    os.system("mkdir {}/output/".format(y))
    os.system("singularity exec -B {}/input:/flywheel/v0/input -B {}/output:/flywheel/v0/output -H {} sing.sif ./run".format(y,y,os.path.abspath("./")))

#
def unzipOutput(y):
    with ZipFile(y+"/output/" + "fmri_input_fmriqa.zip", 'r') as zipObj:
        zipObj.extractall(y+"/output/")


# Renames the output to coil + date and moves them to the daily/history folders
def renameOutput(y):
    # Gets coil name from .xml output
    root = ET.parse(y+"/output/" + "fmriqa/summaryQA.xml").getroot()
    for child in root[0][1]:
        if child.get('name') == "receivecoilname":
            coil = child.text
        if child.get('name') == "scanner":
            scanner= child.text
        if child.get('name') == 'scandate':
            exp_date = child.text

    dateOutput = finalOutput + "/" + scanner + "_" + coil + "/" + exp_date
    os.renames(y+"/output", dateOutput)
    os.system('scp -r {} {}/{}_{}/'.format(dateOutput, SERVER_OUTPUT, scanner, coil))


main()
