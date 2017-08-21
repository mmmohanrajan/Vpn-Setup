from subprocess import Popen, PIPE
from getpass import getpass

class VpnSetup(object):
    """
    helps to automate vpn connection
    """
    vpn_name = 'vpn'
    vpn_script_path = "/usr/bin/%s.py" % vpn_name
    service_file_path = "/lib/systemd/system/%s.service" % vpn_name

    @staticmethod
    def run_cmd(cmd, error=False):
        """
        running a command in shell
        :param cmd: command want to exc Ex: ls
        :return: list of lines of stdout Ex: ['file1', 'file2'], Note: [] if its error.
        """
        # to make sure shell=True/False depends on given cmd
        shell_flag = True if type(cmd) is str else False
        output = Popen(cmd, shell=shell_flag, stdout=PIPE, stderr=PIPE)
        if error:
            return output.stderr.readlines()
        return output.stdout.readlines()

    @classmethod
    def install_open_connect(cls):
        cmd = "sudo apt-get install openconnect -y"
        if VpnSetup.run_cmd(cmd):
            print "Openconnect installed successfully"

    @classmethod
    def create_vpn_script(cls):
        """
        used to create a script
        :return:
        """
        cls.vpn_name = raw_input("Enter the VPN name:") or cls.vpn_name
        host_name = raw_input("Enter the host name:")
        vpn_group = raw_input("Enter the vpn_group:")
        uname = raw_input("Enter the uname:")
        pwd = getpass("Enter the pwd")
        if filter(lambda x: x == "", [host_name, vpn_group, uname, pwd]):
            print "Any of above field should't empty"
            return None
        script_str = """
from subprocess import Popen, PIPE, STDOUT


host_name = '{0}'
vpn_group = '{1}'
uname = '{2}'
pwd = '{3}'
Popen(['sudo','openconnect', host_name], stdout=PIPE, stdin=PIPE, stderr=PIPE).communicate(input='%s\\n%s\\n%s'%(vpn_group, uname, pwd))\n""".format(host_name, vpn_group, uname, pwd)
        with open(cls.vpn_script_path, 'w+') as f:
            f.writelines(script_str)
        return 'Success'

    @classmethod
    def create_service(cls):
        """
        create a linux cuxtom service
        :return:
        """
        # Restart = always
        # RestartSec = 10
        script_str = """
[Unit]
Description=%s

[Service]
Type=simple
ExecStart=/usr/bin/python %s
        """ % (cls.vpn_name, cls.vpn_script_path)
        with open(cls.service_file_path, 'w+') as f:
            f.writelines(script_str)

        # reload systemctl
        cls.run_cmd('systemctl daemon-reload')
        print "Successfully created %s service" % cls.vpn_name
        print "sudo service %s status" % cls.vpn_name
        print "sudo service %s start" % cls.vpn_name
        print "sudo service %s stop" % cls.vpn_name
        print "sudo service %s restart" % cls.vpn_name

    @classmethod
    def main(cls):
        """
        main prgm to start
        :return:
        """
        if not VpnSetup.run_cmd('openconnect -V'):
            cls.install_open_connect()
        if cls.create_vpn_script():
            cls.create_service()

if __name__ == '__main__':
    VpnSetup.main()
