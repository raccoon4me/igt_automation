from __future__ import with_statement
from fabric.tasks import execute
from optparse import OptionParser
from fabric.colors import green, red, blue, yellow
from termcolor import colored
from datetime import datetime, timedelta
from collections import OrderedDict
from operator import itemgetter
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
import re


sys.stdout.flush()
#little rule to stdout the info level
logging.getLogger().setLevel(logging.INFO)
logger1 = logging.getLogger('_')

def parser():
    usage_array = []
    usage_array.append("python main_expire-tapes.py [-e environement] [-s server] [-d days] [-x password]")
    parser = OptionParser(usage="".join(usage_array), version="0.1-1")
    parser.add_option("-e", "--environement",
                      dest="environement",
                      help="Possible options: [gy] [gi]")
    parser.add_option("-s", "--servers",
                      dest="servers",
                      help="Possible options: [bkp01]")
    parser.add_option("-d", "--days",
                      dest="days",
                      help="int")
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

class filterlogs(object):
    #declare my member variables
    now = datetime.now()
    dateNow = datetime.strptime('%s %s %s' % (now.month,now.day,now.year),'%m %d %Y')
    def __init__(self,my_ouput):
        self.my_ouput = my_ouput

    def initdateFutur(self,days):
        self.dateFutur = self.dateNow + timedelta(days=int(days))

    def general_filtering(self):
        x= []
        for line in self.my_ouput.split('\n'):
            #we clean the line
            cleanLine = line.strip()
            #as long as we have a line which is not empty, let's print them
            if cleanLine:
                #let's clean each line
                if ('Executing' not in cleanLine) and ('PASS' not in cleanLine) and ('Done' not in cleanLine) and ('Disconnecting' not in cleanLine):
                    #use regular expression to clean the weird caracters such as x1b etc...
                    cleanLine = re.sub('\x1b.*?m', '', cleanLine)
                    #z = " ".join(cleanLine.split()).split(' ')[0]," ".join(cleanLine.split()).split(' ')[1]
                    #for each splitted line we found, we add it to x
                    x.append(cleanLine)
        return x

    def goingdeeper(self,x):
        data = {}
        i = 0
        for line in x:
            tapes =  " ".join(line.split()).split(' ')[0]
            dates = " ".join(line.split()).split(' ')[2]

            dates = datetime.strptime('%s %s %s' % (dates.split('/')[0],dates.split('/')[1],dates.split('/')[2]),'%m %d %Y')
            #on compare
            if dates.date() >= self.dateNow.date() and dates.date() <=  self.dateFutur.date():
                #on met tout ca dans un dict
                data[tapes] = dates.strftime('%b %d %Y')
                #we increment i for knowing the number of availables tapes in total
                i = i+1
        d = OrderedDict(sorted(data.items(), key=itemgetter(1)))
        if i > 0:
            logging.info("From %s to %s, %s tape(s) are candidates for being expired" % (self.dateNow.strftime('%d %b %Y'),
                                                                                         self.dateFutur.strftime('%d %b %Y'),i))
            return d
        else:
            logging.info("There is no candidate tape to be expired for this range of time")
            return False

class filterexpireoutput(filterlogs):

    def __init__(self):



'''
class filtermd5ouput(filterlogs):

'''


def main_process(opts):

    isfileexist(opts.environement + '.cfg')
    writeToConfigFile(opts.environement, 'login', 'my_password', opts.password)

    now = datetime.now()

    dateNow = datetime.strptime('%s %s %s' % (now.month,now.day,now.year),'%m %d %Y')
    #we define the delta here
    dateFutur = dateNow + timedelta(days=int(opts.days))

    #for storing the expirable tapes
    data = {}
    i = 0
    p = subprocess.check_output('fab -f deploy.py -c ' + opts.environement +'.cfg -H '+
                        extractIPFromCfg(opts.environement,'ips',opts.servers)+' expiretapes',stderr=subprocess.STDOUT,shell=True)
    new_output = filterlogs(p)
    new_output.initdateFutur(opts.days)
    ww = new_output.goingdeeper(new_output.general_filtering())
    if ww != False:
        for key, value in ww.iteritems():
            logging.info("Tape %s as its expired the %s" % (key, value))


    '''
    new_output.general_filtering()
    if new_output.goingdeeper() != False:
        for key, value in new_output.goingdeeper().iteritems():
            logging.info("Tape %s as its expired the %s" % (key, value))
    '''
    #we read the subprocess stdout
    #for each real line
    '''
    for line in p.split('\n'):
        #si la line contient expires
        if ('expires' in line):
            #on split tout ca et on attribue les variables
            tapes =  " ".join(line.split()).split(' ')[0]
            dates = " ".join(line.split()).split(' ')[2]
            #on prends toutes les dates qui sont juste des strings et on les converties en vrai date afin de faire de vrai comparaisons entre dates
            dates = datetime.strptime('%s %s %s' % (dates.split('/')[0],dates.split('/')[1],dates.split('/')[2]),'%m %d %Y')
            #on compare
            if dates.date() >= dateNow.date() and dates.date() <=  dateFutur.date():
                #on met tout ca dans un dict
                data[tapes] = dates.strftime('%b %d %Y')
                #we increment i for knowing the number of availables tapes in total
                i = i+1


    #we order the dictionnary on the values keys
    d = OrderedDict(sorted(data.items(), key=itemgetter(1)))
    if i > 0:
        logging.info("From %s to %s, %s tape(s) are candidates for being expired" % (dateNow.strftime('%d %b %Y'),dateFutur.strftime('%d %b %Y'),i))
    else:
        logging.info("There is no candidate tape to be expired for this range of time")
        #very nice for accessing all the option of a dict, key and value
    for key, value in d.iteritems():
        logging.info("Tape %s as its expired the %s" % (key, value))
    '''

    writeToConfigFile(opts.environement, 'login', 'my_password', '')
    sys.exit(0)

def main():
    # Parser inputs
    opts = parser()
    #Detect signal Ctrl
    signal.signal(signal.SIGINT, signal_handler)
    main_process(opts)

if __name__ == '__main__':
    main()
