from fabric.api import *
from fabric.contrib.files import append
from fabric.context_managers import cd
from xmlrpclib import ServerProxy
env.hosts=["zenoss1", "zenoss2",'agent1', 'agent2']
env.user="root"
env.password="gogslab"
DIR = "/root/"
def is_Installed(package):

        """Get the status of a package
        given a package-name.
        """
        with settings(warn_only=True):
                result = run("dpkg -s %s | grep Status" % (package))#,capture=True)
                print ("result = ", result)
                print("return_code = ",result.return_code)
                if result.return_code == int("1"):
                        return 1
                return 0
def get(url):
        """ Perform wget to the url given  """
        with settings(warn_only=True):
                with cd(DIR):
                        run("wget %s" % url)
                        run("chmod +x zo425_ubuntu-debian.sh")
def update():
        """ Update content of /etc/apt/sources.list file and /etc/hosts file
            do apt-get update"""
        with settings(warn_only=True):
                append("/etc/apt/sources.list","deb http://fr.archive.ubuntu.com/ubuntu precise main multiverse",use_sudo=True)
                append("/etc/hosts","127.0.0.1 ubuntu",use_sudo=True)
                run("apt-get update -y")
def javaInstall():
        """ For silent Installation of  oracle java-7 also modify apt repository so that java installation process will not ask for license"""
        with settings(warn_only=True):
                sudo("add-apt-repository -y ppa:webupd8team/java")
                sudo("apt-get update -y")
                sudo("echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections")
                sudo("echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections")
                sudo("apt-get -y install oracle-java7-installer")
                
                @task
@hosts('agent1')
def addHostToMonitor(ip):
        print("Adding monitoring host")

        url = ('http://10.43.4.235:8080/zport/dmd/DeviceLoader?deviceName=%s&devicePath=/Server/Linux&loadDevice:method=1'%(ip))
        print(url)
        local("curl -u admin:zenoss '%s'"%( url))
@task
@hosts('zenoss2')
def install():
        ''' Install Zenoss and dependancy packages for zenoss
        '''
        packages = ["openjdk-6-jre", "libxslt-dev", "libgtk2.0-0:i386", "libsnmp9-dev",  "-f -q", "snmp", "snmp-mibs-downloader", "snmpd"]#, "-q mysql-server"]
        javaInstall()
        update()
        sudo("export DEBIAN_FRONTEND=noninteractive")
        for package in packages:
                if is_Installed(package)== 1 :
                        print ("package %s is not installed so that installing it." % package)
                        sudo("apt-get install %s -y" % (package))
                else:
                        print ("package %s is installed" % package)
        get("--no-check-certificate https://raw.github.com/hydruid/zenoss/master/core-autodeploy/4.2.5/zo425_ubuntu-debian.sh")

        with settings(warn_only=True):
                result = run("% n | ./zo425_ubuntu-debian.sh 2>&1 | tee script-log.txt")
                print("retirn code of script = ",result.return_code)

@task
@parallel
@hosts('agent1')
def agent():
        ''' Install snmp agent on monitoring machines
        '''
        print("Agent configuration bigin...!")
        update()
        packages = ["snmp", "snmp-mibs-downloader", "snmpd"]
        for package in packages:
                if is_Installed(package)== 1 :
                        print ("package %s is not installed so that installing it." % package)
                        sudo("apt-get install %s -y" % (package))
                else:
                       print ("package %s is installed" % package)
        with settings(warn_only=True):
                result = run("download-mibs")
                print("return code of agent = ",result.return_code)
                put('/home/supriya/py-sup/snmpd.conf','/etc/snmp/',use_sudo=True)


def hostname():
        run("hostname")
def hello2():
        print("hello world.............!!!!!!!!")
