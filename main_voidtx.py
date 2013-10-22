from __future__ import with_statement
from fabric.tasks import execute
from optparse import OptionParser
from fabric.colors import green, red, blue, yellow
from termcolor import colored
from fabric.api import *
import sys
import os
import time
import signal
import subprocess
import ConfigParser
import time
import logging
import Colorer



sys.stdout.flush()
#little rule to stdout the info level
logging.getLogger().setLevel(logging.INFO)
logger1 = logging.getLogger('_')
txdict = []

#------------------------#
PATH_FAB_FILE = '/var/lib/jenkins/workspace_bin/DEPLOY_RELEASE_FROM_SAN_FRANCISCO_OPS01'

#this function is parsing the parameters and make test that the input
def parser():
    usage_array = []
    usage_array.append("python deploy.py [-e environement] [-s server] [-z status] [-t tansaction] [-x password]")
    parser = OptionParser(usage="".join(usage_array), version="0.1-1")
    parser.add_option("-e", "--environement",
                      dest="environement",
                      help="Possible options: [gy] [gi]")
    parser.add_option("-s", "--servers",
                      dest="servers",
                      help="Possible options: [sdb05] [sdb06] ...")
    parser.add_option("-t", "--transaction",
                      dest="transaction",
                      help="9 digits - ex:786539695")
    parser.add_option("-z", "--status",
                      dest="status",
                      help="progress|pending")
    parser.add_option("-x", "--password",
                      dest="password",
                      help="Your Password")

    ## check not empty parser.add_options
    (opts, args) = parser.parse_args()
    return opts


def signal_handler(signal, frame):
    print colored('You just pressed Ctrl+C! Please wait while the program is terminating...', 'red')
    #TO BE IMPLEMENTED
    #rollback()
    time.sleep(2)
    # Exit
    sys.exit(0)

#this function read the cfg file and will return the x indice of the desired ips for the desired app,web,rng,db servers
def extractIPFromCfg(aENV,aSection,aSubsection):
    #this one will retrive the app from the app01 string, it will be needed for creating the good index for the ips
    #so does the :3
    aServer = aSubsection
    aSubsection = aServer[:3]+'_server_hosts'
    #to select between app01,02,03,04 .. from ips1;ip2, we retrive only the 1 or 2 or 3 or 4 from app0x word
    anIndice = aServer[4:]
    ConfFile = aENV + '.cfg'
    config = ConfigParser.RawConfigParser()
    config.read(ConfFile)
    #to select between app01,02,03,04 .. from ips1;ip2, the -1 is because the app01 is the first and
    #as wel all know, this things start at 0
    return config.get(aSection,aSubsection).split(';')[int(anIndice)-1]

#if the file can't be found, exit code 1
def isfileexist(Myfile):
    try:
        with open(Myfile):
            pass
    except IOError:
        print 'File %s not Found !! Exiting...' % Myfile
        sys.exit(1)

#this func receive gi, one section from gi.cfg, one subsection from section from gi.cfg, onee release PaTH/password. whatever
def writeToConfigFile(oneENV, oneSection, oneSubSection, onePATH):
    #we concat gi+.cfg to create {gi.gy}.cfg
    ConfFile = oneENV + '.cfg'
    #init of reading func config.raw
    config = ConfigParser.RawConfigParser()
    #reading the file
    config.read(ConfFile)
    #we set for one section, one subsection
    config.set(oneSection, oneSubSection, onePATH)
    #writting...
    with open(ConfFile, 'wb') as configfile:
        config.write(configfile)


def main_process(opts):
    os.chdir(PATH_FAB_FILE)
    #we write to the config file
    isfileexist(opts.environement + '.cfg')
    writeToConfigFile(opts.environement, 'login', 'my_password', opts.password)
    os.chdir(PATH_FAB_FILE)

    #Telnet from local to San franscisco to port 22
    logger1.info("/-----------------------------------------------------------------------------------------------/")
    logging.info("TESTING PORT 22 FROM YOUR MACHINE TO %s" % opts.servers.upper())
    p = subprocess.call('fab -f deploy.py -c ' + opts.environement +'.cfg ConnectivityCheckTelnet:sdb',shell=True)
    logging.info("/-----------------------------------------------------------------------------------------------/")
    logging.info("VOIDING IN %s TRANSACTION ID N %s ON SERVER %s IN DATACENTER [%s]:" %
                 (opts.status.upper(),opts.transaction,opts.servers.upper(),opts.environement.upper()))
    #in case we have a lot of tx to void (tx1,tx2,tx3)
    txdict = opts.transaction.split(',')
    for onetx in txdict:
         p = subprocess.call('fab -f deploy.py -c '+opts.environement+'.cfg -H '+
                        extractIPFromCfg(opts.environement,'ips',opts.servers)
                        +' voidtx:%s,%s' % (onetx,opts.status),shell=True)
         time.sleep(2)


    #we reset the variables again to null
    writeToConfigFile(opts.environement, 'login', 'my_password', '')
    logging.info("JOB DONE...")
    sys.exit(0)

def main():
    # Parser inputs
    opts = parser()
    #Detect signal Ctrl
    signal.signal(signal.SIGINT, signal_handler)
    main_process(opts)

if __name__ == '__main__':
    main()





