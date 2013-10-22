from fabric.api import *
from fabric.contrib.files import exists
from fabric.colors import green,red, blue
from fabric.utils import error,warn
from decimal import Decimal
from socket import *
import os
import sys

#VARs, dictionnaries for storing everything !
env.roledefs = {'sf':[], 'dep':[], 'app':[], 'web':[], 'rng':[], 'sdb':[], 'ver':[], 'log':[]}

### very local vars
local_path = '/var/lib/jenkins/workspace_bin/DEPLOY_RELEASE_FROM_SAN_FRANCISCO_OPS01/logs/'

######### the local Vars that will be used along the way of this script

env.user = env.my_user
localPath = env.local_folder_release
env.password = env.my_password
releasePath = env.folder_release
wworks_User = env.env_wworks
db_user = env.env_db
backup_User = env.env_backup
env.shell = "/bin/bash -c"


#########
g_apache_dir = os.path.join('/wworks/rgs/apache',env.env_name)
g_weblogic_dir = os.path.join('/wworks/rgs/weblogic',env.env_name)
g_rng_dir = os.path.join('/wworks/rgs/tomcat',env.env_name)
g_deployer_dir = os.path.abspath('/wworks/rgs/deployer/services/RGS/etc')

#########

#internal functions
def parse_path(path):
    matching = [s for s in path.split('/') if 'RELEASE' in s]
    return matching[0]
###########

if env.has_key('sf_server_hosts'):
    env.roledefs['sf'] = env.sf_server_hosts.split(';')

if env.has_key('dep_server_hosts'):
    env.roledefs['dep'] = env.dep_server_hosts.split(';')

if env.has_key('app_server_hosts'):
    env.roledefs['app'] = env.app_server_hosts.split(';')

if env.has_key('web_server_hosts'):
    env.roledefs['web'] = env.web_server_hosts.split(';')

if env.has_key('rng_server_hosts'):
    env.roledefs['rng'] = env.rng_server_hosts.split(';')

if env.has_key('sdb_server_hosts'):
    env.roledefs['sdb'] = env.sdb_server_hosts.split(';')

if env.has_key('ver_server_hosts'):
    env.roledefs['ver'] = env.ver_server_hosts.split(';')

if env.has_key('log_server_hosts'):
    env.roledefs['log'] = env.log_server_hosts.split(';')

###########

@task
def RollOverControlWebServers(service="stop"):
    ''' Stop/Start/Restart web servers '''
    apache_bin_path = os.path.join(g_apache_dir, 'bin')
    with cd(apache_bin_path):
        if exists('apachectl_v2'):
            run('chmod u+x apachectl_v2')
            if service.lower()=="stop":
                run('./apachectl_v2 stop')
            elif service.lower()=="start":
                run('nohup ./apachectl_v2 start | tee ../logs/nohup.out')
            elif service.lower()=="restart":
                run('./apachectl_v2 stop')
                run('nohup ./apachectl_v2 start | tee ../logs/nohup.out')
            else:
                error('Invalid service type')
        else:
            run('echo apachectl_v2 does not exist! Possibility first deloyment')

@task
def RollOverControlAppServers(service="stop"):
    ''' Stop/Start/Restart/State weblogic admin servers '''
    print service
    weblogic_bin_path = os.path.join(g_weblogic_dir, 'bin')
    with cd(weblogic_bin_path):
        if service.lower()=="stop":
            sudo('./weblogic.admin.managed stop',user=wworks_User)
            sudo('./weblogic.platform.managed stop',user=wworks_User)
            print('[%s]' % (blue("PASS")))
        elif service.lower()=="start":
            sudo('nohup ./weblogic.admin.managed start | tee ../logs/nohup.out',user=wworks_User)
            sudo('nohup ./weblogic.platform.managed start | tee ../logs/nohup.out',user=wworks_User)
            print('[%s]' % (blue("PASS")))
        elif service.lower()=="restart":
            sudo('./weblogic.admin.managed stop',user=wworks_User)
            sudo('./weblogic.platform.managed stop',user=wworks_User)
            sudo('nohup ./weblogic.admin.managed start | tee ../logs/nohup.out',user=wworks_User)
            sudo('nohup ./weblogic.platform.managed start | tee ../logs/nohup.out',user=wworks_User)
            print('[%s]' % (blue("PASS")))
        elif service.lower()=="state":
            sudo('./weblogic.admin.managed state',user=wworks_User)
            sudo('./weblogic.platform.managed state',user=wworks_User)
            print('[%s]' % (blue("PASS")))
        else:
            error('Invalid service type')

@task
def RollOverControlAppAdminServers(service="stop"):
    ''' Stop/Start/Restart/State weblogic admin servers '''
    weblogic_bin_path = os.path.join(g_weblogic_dir, 'bin')
    with cd(weblogic_bin_path):
        if service.lower()=="stop":
            sudo('./weblogic.admin.admin stop',user=wworks_User)
            sudo('./weblogic.platform.admin stop',user=wworks_User)
        elif service.lower()=="start":
            sudo('nohup ./weblogic.admin.admin start | tee ../logs/nohup.out',user=wworks_User)
            sudo('nohup ./weblogic.platform.admin start | tee ../logs/nohup.out',user=wworks_User)
        elif service.lower()=="restart":
            sudo('./weblogic.admin.admin stop',user=wworks_User)
            sudo('./weblogic.platform.admin stop',user=wworks_User)
            sudo('nohup ./weblogic.admin.admin start | tee ../logs/nohup.out',user=wworks_User)
            sudo('nohup ./weblogic.platform.admin start | tee ../logs/nohup.out',user=wworks_User)
        elif service.lower()=="state":
            sudo('./weblogic.admin.admin state',user=wworks_User)
            sudo('./weblogic.platform.admin state',user=wworks_User)
        else:
            error('Invalid service type')

@task
def ControlWebServers(service="stop"):
    ''' Stop/Start web servers '''
    apache_bin_path = os.path.join(g_apache_dir, 'bin')
    with cd(apache_bin_path):
        if exists('apachectl_v2'):
            run('chmod u+x apachectl_v2')
            if service.lower()=="stop":
                run('./apachectl_v2 stop')
            elif service.lower()=="start":
                run('nohup ./apachectl_v2 start | tee ../logs/nohup.out')
            else:
                error('Invalid service type')
        else:
            run('echo apachectl_v2 does not exist! Possibility first deloyment')

@task
def ControlAppAdminServers(service="stop"):
    ''' Stop/Start weblogic admin servers '''
    weblogic_bin_path = os.path.join(g_weblogic_dir, 'bin')
    with cd(weblogic_bin_path):
        if service.lower()=="stop":
            run('./weblogic.admin.admin stop')
            run('./weblogic.platform.admin stop')
        elif service.lower()=="start":
            run('nohup ./weblogic.admin.admin start | tee ../logs/nohup.out')
            run('nohup ./weblogic.platform.admin start | tee ../logs/nohup.out')
        else:
            error('Invalid service type')

@task
def ControlAppServers(service="stop"):
    ''' Stop/Start weblogic managed servers '''
    weblogic_bin_path = os.path.join(g_weblogic_dir, 'bin')
    with cd(weblogic_bin_path):
        if service.lower()=="stop":
            run('./weblogic.admin.managed stop')
            run('./weblogic.platform.managed stop')
        elif service.lower()=="start":
            run('nohup ./weblogic.admin.managed start | tee ../logs/nohup.out')
            run('nohup ./weblogic.platform.managed start | tee ../logs/nohup.out')
        else:
            error('Invalid service type')

@task
def ControlRNGServers(service="stop"):
    ''' Stop/Start rng servers '''
    rng_bin_path = os.path.join(g_rng_dir, 'bin')
    with cd(rng_bin_path):
        if exists('tomcat.rng'):
            run('chmod u+x tomcat.rng')
            if service.lower()=="stop":
                run('./tomcat.rng stop')
            elif service.lower()=="start":
                run('nohup ./tomcat.rng start | tee ../logs/nohup.out')
            else:
                error('Invalid service type')
        else:
            run('echo run_tomcat.sh does not exist! Possibility first deloyment')

@task
def ConnectivityCheck():
    ''' Check conectivity from the running host to various hosts '''
    with settings(hide('warnings','running','stdout','stderr','status'),warn_only=True):
        result = local('ping -q -c 2 %s' % env.host)
        if result.failed:
            print('\tConnection to %s: [%s]' % (env.host,red("FAIL")))
        else:
            print('\tConnection to %s: [%s]' % (env.host,blue("PASS")))


@task
def ConnectivityCheckTelnet(*my_environement):
    for eachtype in my_environement:
        for eachHost in env.roledefs[eachtype]:
            try:
                s = socket(AF_INET, SOCK_STREAM)
                s.settimeout(1.4)
                s.connect((eachHost, 22))
                print('\tConnection to %s on port 22: [%s]' % (eachHost,blue("PASS")))
            except:
                print('\tConnection to %s on port 22: [%s]' % (eachHost,red("FAIL")))

@task
def ConnectionFromHostToHostsTelnet(*my_environement):
    with settings(hide('warnings','running','stdout','stderr','status'),warn_only=True):
        #justified for the * of my_environement, eachType can take app,web,db etc...
        for eachtype in my_environement:
            for eachHost in env.roledefs[eachtype]:
                result = run('nc -z %s 22' % eachHost)
                if result.failed:
                    print('\tConnection from %s to %s: [%s]' % (env.host, eachHost, red("FAIL")))
                else:
                    print('\tConnection from %s to %s: [%s]' % (env.host, eachHost, blue("PASS")))

@task
def ConnectionFromHostToHosts(*my_environement):
    with settings(hide('warnings','running','stdout','stderr','status'),warn_only=True):
        #justified for the * of my_environement
        for eachtype in my_environement:
            for eachHost in env.roledefs[eachtype]:
                result = run('ping -q -c 2 %s' % eachHost)
                if result.failed:
                    print('\tConnection from %s to %s: [%s]' % (env.host, eachHost, red("FAIL")))
                else:
                    print('\tConnection from %s to %s: [%s]' % (env.host, eachHost, blue("PASS")))
@task
def checkmd5SF():
    with settings(hide('warnings','running','stdout','stderr','status'),warn_only=True):
        with cd(releasePath):
            '''
            print "Release number:%s" % blue(parse_path(releasePath,5))
            print "Release Type:%s" % blue(parse_path(releasePath,4))
            response = raw_input(red("Are those information correct(yes/no)?"))
            if response != 'yes':
                print red("Exiting...")
                sys.exit(0)
            else:
                pass
             '''
            result = run('for i in $(ls); do md5sum $i;done')
            print blue(result)
            if result.failed:
                print('[%s]' % (red("FAIL")))
            else:
                print('[%s]' % (blue("PASS")))
@task
def checkmd5():
    with settings(hide('warnings','running','stdout','stderr','status'),warn_only=True):
        with cd(localPath+parse_path(releasePath)):
            result = run('for i in $(ls); do md5sum $i;done')
            print blue(result)
            if result.failed:
                print('Couldn\'t locate the files in %s: [%s]' % (localPath+parse_path(releasePath,5),red("FAIL")))
            else:
                print('[%s]' % (blue("PASS")))
@task
def scpThis():
    with settings(hide('warnings','running','stdout','stderr','status'),warn_only=True):
        try:
            result = run('scp -r %s %s:%s' % (releasePath,env.roledefs['dep'],localPath))
            print('\tSending file(s) from %s to %s [%s]:' % (env.host,env.roledefs['dep'],blue("PASS")))
        except:
            print('\tSending file(s) from %s to %s [%s]:' % (env.host,env.roledefs['dep'],red("FAIL")))

@task
def deploy(*my_environement):
    with settings(hide('warnings','running','stdout','stderr','status'),warn_only=True):
        for eachtype in my_environement:
            for eachHost in env.roledefs[eachtype]:
                try:
                    result = sudo('scp -r %s %s:%s' % (localPath+parse_path(releasePath),eachHost,localPath),user='wworks')
                    print('\t Sending file(s) from %s to %s: [%s]' % (env.host,eachHost,blue("PASS")))
                    pass
                except:
                    print('\t Sending file(s) from %s to %s: [%s]' % (env.host,eachHost,red("FAIL")))

#first, before doing anything and loosing time... check size
@task
def DiskSpaceCheck():
    ''' Check free disk spaces '''
    with settings(hide('warnings','running','stdout','stderr','status'),warn_only=True):
        result = run('df -h %s | tail -1 | awk \'{print $3}\'' % env.DISCSPACE_VOL_NAME_FILTER)
        print result
        hostDiskSize = float((result.split('\n')[-1])[:-1])
        freeDiskSize = float(env.DISCSPACE_RESERVE_SIZE)
        if hostDiskSize <= freeDiskSize:
            print('\tDisk space check on host %s: [%s]' % (env.host,red("FAIL")))
            print('\tFree space size:%3.1f Need:%3.1f' % (hostDiskSize,freeDiskSize))
            sys.exit(status=1)
        else:
            print('\tDisk space check on host %s: [%s]' % (env.host,green("PASS")))
            print('\tFree space size:%3.1f' % (hostDiskSize))

@task
def checkipsquova(oneip,env):
    #with settings('warnings','running','stdout','stderr','status'):
        #because GI and GY difference
    if env == 'gi':
        onePath = '/wworks/quova/ver_6.2/samples'
        with path('/opt/jdk1.5.0_09/bin'):
            with cd(onePath):
                try:
                    sudo('./quovaj SimpleSample  %s' % oneip,user=wworks_User)
                    print('\t Checking ip %s [%s]' % (oneip,blue("PASS")))
                except:
                    print('\t Checking ip %s [%s]' % (oneip,red("FAIL")))
    else:
        onePath = '/wworks/quova/ver_6.2/api/samples'
        with cd(onePath):
            try:
                sudo('./quovaj SimpleSample %s' % (oneip),user=wworks_User)
                print('\t Checking ip %s [%s]' % (oneip,blue("PASS")))
            except:
                print('\t Checking ip %s [%s]' % (oneip,red("FAIL")))
@task
def voidtx(onetx,status):
    #with settings(hide('warnings','running','stderr','status'),warn_only=True):
        #because GI and GY difference
    if status == 'progress':
        '''
        with shell_env(ORACLE_BASE='/usr/pkg/oracle',
                       ORACLE_DB='rgsgib',
                       ORACLE_HOME='/usr/pkg/oracle/product/10.2.0/db',
                       ORACLE_SID='rgsgib2',
                       ORA_CRS_HOME='/usr/pkg/oracle/product/10.2.0/crs',
                       ORA_NLS10='/usr/pkg/oracle/product/10.2.0/db/nls/data',
                       PATH='/usr/pkg/oracle/product/10.2.0/db/bin:/usr/kerberos/bin:/usr/local/bin:/bin:/usr/bin:/oracle/scripts:/usr/pkg/oracle/product/10.2.0/db/OPatch'):
        '''
        with cd('/oracle/scripts'):
            try:
                #sudo('env',user=db_user)
                #sudo('env %s' % onetx,user=db_user)
                sudo('/usr/pkg/oracle/product/10.2.0/db/bin/sqlplus rgsapp/rgsapp @/oracle/scripts/void_txn.sql %s' % onetx,user=db_user)
                print('\t Voiding IN PROGRESS Transaction ID %s [%s]' % (onetx,blue("PASS")))
            except:
                print('\t Voiding IN PROGRESS Transaction ID %s [%s]' % (onetx,red("FAIL")))
    else:
        with cd('/oracle/scripts'):
            try:
                sudo('./void_xt_pending.sh %s' % onetx,user=db_user)
                print('\t Voiding IN PROGRESS Transaction ID %s [%s]' % (onetx,blue("PASS")))
            except:
                print('\t Voiding IN PROGRESS Transaction ID %s [%s]' % (onetx,red("FAIL")))

@task
def retrievetapes():
    with settings(hide('warnings', 'running', 'stdout', 'stderr'),warn_only=True):
        #because GI and GY difference
        with cd('/home/backup'):
            try:
                t = sudo('./netbackup_offsite.sh -t',user=backup_User)
                for i in t.split(' '):
                    print "/--------------------------------------------/"
                    print "The tape %s need to be taken off site" % i
                    print "/--------------------------------------------/"
                sudo('./netbackup_offsite_move_tapes.sh',user=backup_User)
            except:
                print "Could not complete operation ! Please check the errors!"

@task()
def retrieveLogs(path,file):
    with settings(hide('warnings', 'running', 'stdout', 'stderr'),warn_only=True):
        try:
            #because GI and GY are not having the file at the same place ...
            if file == 'messages' or file == 'secure':
                sudo('cp %s /home/heslous/' % (path+file),user='root')
                sudo('chown -R heslous /home/heslous/%s' % file,user='root')
                get('/home/heslous/%s' % file,local_path+file)
                #run('rm -f /home/heslous/%s' % file)
            else:
                get(path+file,local_path+path.split('/')[6])
        except:
            print "File %s Not Found!!" % (path+file)

@task()
def expiretapes():
    with settings(hide('warnings', 'running', 'stdout', 'stderr'),warn_only=True):
        try:
            r = sudo('/usr/openv/netbackup/bin/admincmd/bpmedialist -summary',user='root')
            for line in r.split('\n'):
                if ('expires') in line:
                    listofexpiredtapes = line
                    print listofexpiredtapes
        except:
            print "file(s) NOT found"



















