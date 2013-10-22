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
import requests


sys.stdout.flush()
#little rule to stdout the info level
logging.getLogger().setLevel(logging.INFO)


#------------------------#
PATH_FAB_FILE = '/var/lib/jenkins/workspace_bin/DEPLOY_RELEASE_FROM_SAN_FRANCISCO_OPS01'

#this function is parsing the parameters and make test that the input
def parser():
    usage_array = []
    usage_array.append("python main_cacti-maps.py [-e environement] [-s server] [-l level] [-a skins] [-x password]")
    parser = OptionParser(usage="".join(usage_array), version="0.1-1")
    parser.add_option("-e", "--environement",
                      dest="environement",
                      help="Possible options: [gy] [gi]")
    parser.add_option("-s", "--servers",
                      dest="servers",
                      help="Possible options: [app01] [app02] [app03] [app04] [all]")
    parser.add_option("-l", "--level",
                      dest="level",
                      help="OFF|FATAL|ERROR|WARN|INFO|DEBUG|TRACE|ALL")
    parser.add_option("-a", "--skin",
                      dest="skin",
                      help="skins....")
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

def extractIPFromCfg2(aENV,aSection,aSubsection):
    #this one will retrieve the app from the app01 string, it will be needed for creating the good index for the ips
    #so does the :3
    aServer = aSubsection
    aSubsection = aServer+'_server_hosts'
    ConfFile = aENV + '.cfg'
    config = ConfigParser.RawConfigParser()
    config.read(ConfFile)
    #to select between app01,02,03,04 .. from ips1;ip2, the -1 is because the app01 is the first and
    #as wel all know, this things start at 0
    return config.get(aSection,aSubsection)

#this function read the cfg file and will return either cacti login, either password
def extractCactiFromCfg(aENV,aParam):
    #this one will retrive the rom the app01 string, it will be needed for creating the good index for the ips
    #so does the :3
    aSubsection = 'cacti_%s' % aParam
    #to select between app01,02,03,04 .. from ips1;ip2, we retrive only the 1 or 2 or 3 or 4 from app0x word

    ConfFile = aENV + '.cfg'
    config = ConfigParser.RawConfigParser()
    config.read(ConfFile)
    #to select between app01,02,03,04 .. from ips1;ip2, the -1 is because the app01 is the first and
    #as wel all know, this things start at 0
    return config.get('login',aSubsection)

#this function read the cfg file and will return the x indice of the desired ips for the desired app,web,rng,db servers


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

def getMyCookie(environement,username,password):
    payload = {'login_username': username, 'login_password': password, 'action':'submit'}
    #we go to the config file to search for the ip regarding the env

    r = requests.get("http://%s/cacti/plugins/weathermap/weathermap-cacti-plugin.php" % extractIPFromCfg2(environement, 'ips','mon'), params=payload)
    return r.headers['set-cookie'].split(';')[0].split('=')[1]

def main_process(opts):
    #we write to the config file
    isfileexist(opts.environement + '.cfg')
    cookie =  getMyCookie(opts.environement,extractCactiFromCfg(opts.environement,'username'),extractCactiFromCfg(opts.environement,'password'))

    #p = subprocess.call('curl -o /home/jthemovie/Pictures/GI_cacti_weather_map_\`date +%Y-%m-%d_%H-%M-%S\`.png \'http://192.168.190.15/cacti/plugins/weathermap/weathermap-cacti-plugin.php?action=viewimage&id=548399b9976a5e8248f9\'' % cookie ,shell=True)
    print 'curl -o /home/jthemovie/Pictures/GI_cacti_weather_map_date.png http://192.168.190.15/cacti/plugins/weathermap/weathermap-cacti-plugin.php?action=viewimage&id=548399b9976a5e8248f9 -H Cookie: Cacti=%s' % cookie


    #we reset the variables again to null
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



