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
import re

sys.stdout.flush()
#little rule to stdout the info level
logging.getLogger().setLevel(logging.INFO)

#------------------------#
sf_deployer = 'sf'
sf_deployer_host = 'ops01.sf'
PATH_FAB_FILE = '/var/lib/jenkins/workspace_bin/DEPLOY_RELEASE_FROM_SAN_FRANCISCO_OPS01'

#this function is parsing the parameters and make test that the input
def parser():
    usage_array = []
    usage_array.append("python deploy.py [-p path] -e environement] [-s servers] [-x password]")
    parser = OptionParser(usage="".join(usage_array), version="0.1-1")
    parser.add_option("-p", "--path",
                      dest="path",
                      help="Put the full path of the folder release in sf01        ex: /home/deploy/prod_dropzone/InternetConsole/RELEASE12697")
    parser.add_option("-e", "--environement",
                      dest="environement",
                      help="Possible options : [gy] [gi] [ka]")
    parser.add_option("-s", "--servers",
                      dest="servers",
                      help="Possible options : [web] [app] [rng] [db]")
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


def isfileexist(Myfile):
    try:
        with open(Myfile):
            pass
    except IOError:
        print 'File %s not Found !! Exiting...' % Myfile
        sys.exit(1)

#function that read and write the cfg file
def writeToConfigFile(oneENV, oneSection, oneSubSection, onePATH):
    ConfFile = oneENV + '.cfg'
    try:
        with open(ConfFile):
            config = ConfigParser.RawConfigParser()
            config.read(ConfFile)
            config.set(oneSection, oneSubSection, onePATH)
            with open(ConfFile, 'wb') as configfile:
                config.write(configfile)
    except IOError:
        print 'File %s not Found !! Exiting...' % ConfFile
        sys.exit(1)

#this function is receiving some raw output from check_output of subprocess, it will clean it and analyze it
def analysemethisoutputandcleanit(somestdout):

    #we will store the list of md5files in a dictionnary
    x = []
    #we will print all md5 in one dict for further analyze of inconsistencies
    keys = []
    #we define that from the ouput, each \n is considered as an end of line
    for line in somestdout.split('\n'):
        #we clean the line
        cleanLine = line.strip()
        #as long as we have a line which is not empty, let's print them
        if cleanLine:
            #let's clean each line
            if ('Executing' not in cleanLine) and ('PASS' not in cleanLine) and ('Done' not in cleanLine) and ('Disconnecting' not in cleanLine):
                #use regular expression to clean the weird caracters such as x1b etc...
                cleanLine = re.sub('\x1b.*?m', '', cleanLine)
                #we split the line for putting in variable in such a form as z = 'md5','files'
                z = " ".join(cleanLine.split()).split(' ')[0]," ".join(cleanLine.split()).split(' ')[1]
                #for each splitted line we found, we add it to x
                x.append(z)
    #we put only the md5 into the dict key
    for key,value in x:
        keys.append(key)
    #this line will tell us how many times appear each items, like a sort, count ex ; md5_1 = 5, md5_2, 5
    result_dict = dict( [ (i, keys.count(i)) for i in set(keys) ] )
    #here we specify that we care only about the values of the result_dict, and technically, if they are all
    #consistent, the len of the set function should return only 1
    #otherwise set will look like this: ex: set([1, 3, 4]),so the len here will be 3, not 1
    if len(set(result_dict.values())) != 1:
        logging.info("func SET: THE MD5SUM IS NOT CONSISTENT %s ,EXITING !!",set(result_dict.values()))
        sys.exit(0)
    else:
        return x

#compare 2 output of md5s
def comparemethis2list(list1,list2):

    md5list1 = []
    md5list2 = []

    for key,value in list1:
        md5list1.append(key)
    for key,value in list2:
        md5list2.append(key)

    if len(md5list1) != len(md5list2):
        print "We dont start good, the two list doesn't even match in size..."
        return False
    else:
        if len(set(md5list1).intersection(md5list2)) != len(md5list1):
            return False
        else:
            return True

def main_process(opts):
    os.chdir(PATH_FAB_FILE)
    #we write to the config file
    writeToConfigFile(opts.environement, 'login', 'my_password', opts.password)
    writeToConfigFile(opts.environement, 'paths', 'folder_release', opts.path)

    #Telnet from local to San franscisco to port 22
    logging.info("/-----------------------------------------------------------------------------------------------/")
    logging.info("TESTING PORT 22 FROM YOUR MACHINE TO SF")
    p = subprocess.call('fab -f deploy.py -c' + opts.environement + '.cfg ConnectivityCheckTelnet:' + sf_deployer,
                        shell=True)
    logging.info("/-----------------------------------------------------------------------------------------------/")

    logging.info("TESTING PORT 22 FROM SF TO THE DEPLOY MACHINE IN DATACENTER [%s]" % opts.environement.upper())
    p = subprocess.call(
        'fab -f deploy.py -c ' + opts.environement + '.cfg -H ' + sf_deployer_host + ' ConnectionFromHostToHostsTelnet:dep',
        shell=True)
    logging.info("/-----------------------------------------------------------------------------------------------/")
    logging.info("TESTING PORT 22 FROM THE DEPLOY MACHINE IN DATACENTER [%s] TO SERVERS AFFECTED [%s]" % (
        opts.environement.upper(), opts.servers.upper()))
    p = subprocess.call(
        'fab -f deploy.py -c ' + opts.environement + '.cfg -R dep ConnectionFromHostToHostsTelnet:' + opts.servers,
        shell=True)
    logging.info("/-----------------------------------------------------------------------------------------------/")
    logging.info("RETRIEVING MD5SUM FROM SF ")
    p = subprocess.check_output('fab -f deploy.py -c ' + opts.environement + '.cfg -H ' + sf_deployer_host + ' checkmd5SF',
                        stderr=subprocess.STDOUT,shell=True)
    #we send the output for analyse and store ir in the list for further comparaisons
    originalmd5files = analysemethisoutputandcleanit(p)
    for key, value in originalmd5files:
        print key,value
    logging.info("/-----------------------------------------------------------------------------------------------/")
    logging.info("SENDING FILE(S) FROM SF TO THE DEPLOY MACHINE IN DATACENTER [%s]" % opts.environement.upper())
    p = subprocess.call('fab -f deploy.py -c ' + opts.environement + '.cfg -H ' + sf_deployer_host + ' scpThis',
                        shell=True)
    logging.info("/-----------------------------------------------------------------------------------------------/")

    logging.info("RETRIEVING MD5SUM FROM THE DEPLOY MACHINE IN DATACENTER [%s]" % opts.environement.upper())
    pa = subprocess.check_output('fab -f deploy.py -c ' + opts.environement + '.cfg -R dep checkmd5',
                                stderr=subprocess.STDOUT,shell=True)
    md5fromdeployer = analysemethisoutputandcleanit(pa)
    for key, value in md5fromdeployer:
        print key,value
    if comparemethis2list(originalmd5files,md5fromdeployer) == False :
        logging.info("Md5 mismtach, exiting...")
        sys.exit(0)
    logging.info("/-----------------------------------------------------------------------------------------------/")
    logging.info("SENDING FILE FROM THE DEPLOY MACHINE IN DATACENTER [%s] TO SERVERS AFFECTED [%s]" % (
        opts.environement.upper(), opts.servers.upper()))
    p = subprocess.call('fab -f deploy.py -c ' + opts.environement + '.cfg -R dep deploy:' + opts.servers, shell=True)
    logging.info("/-----------------------------------------------------------------------------------------------/")
    logging.info("RETRIEVING MD5SUM FROM THE SERVERS [%s] AFFECTED IN THE DATACENTER [%s]" % (
        opts.servers.upper(), opts.environement.upper()))
    pd = subprocess.check_output('fab -f deploy.py -c ' + opts.environement + '.cfg -R ' + opts.servers + ' checkmd5',
                        stderr=subprocess.STDOUT,shell=True)
    md5fromserver = analysemethisoutputandcleanit(pd)
    for key, value in md5fromserver:
        print key,value

    logging.info("/-----------------------------------------------------------------------------------------------/")
    #we reset the variables again to null
    writeToConfigFile(opts.environement, 'login', 'my_password', '')
    #writeToConfigFile(opts.environement, 'paths', 'folder_release', '')
    logging.info("DEPLOYEMENT FINISHED with SUCCESS !! , EXITING...")
    sys.exit(0)


def main():
    # Parser inputs
    opts = parser()
    #Detect signal Ctrl
    signal.signal(signal.SIGINT, signal_handler)
    main_process(opts)


if __name__ == '__main__':
    main()




