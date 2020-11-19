import subprocess
import pdb

class TPC_util:
    def __init__(self, log, timeout, debug, proxy):
        self.log = log
        self.proxy = proxy
        self.timeout = "-m"+str(timeout)
        self.debug = debug
   
    def get_command_str(self, command):
        command_str = ""
        for i in command:
            command_str+=i+" "
        return command_str[:-1]
 
    def extract_macaroon(self, response):
        self.log.debug("response: "+response)
        macaroon = response.split('"')[3]
        return macaroon
    
    def get_base_command(self):
        command=["curl", "-L", "--capath", "/etc/grid-security/certificates"]
        if(self.debug == 1):
            command = command + ["-s"]
        command = command + [self.timeout]
        command = command + ["-H", 'X-No-Delegate:true', "-H", 'Credential: none']

        return command

    def request_macaroon(self, url, permission_list):
        macaroon = None
        command = self.get_base_command()
        command = command + ["--cacert", self.proxy, "-E", self.proxy]
        command = command + ["-X", "POST"]
        command = command + ["-H", 'Content-Type:application/macaroon-request']
        command = command + ["-d"]
        command = command + ['{"caveats":["activity:'+permission_list+'"], "validity": "PT30M"}']
        command = command + [url]
        
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if out.returncode ==0:
            macaroon = self.extract_macaroon(stdout)
        else:
            self.log.error("Something went wrong when executing command:\n" +self.get_command_str(command))
            self.log.debug("command:"+ self.get_command_str(command))
            self.log.debug("stdout:"+ stdout)
   
        return macaroon
    

    def get_byte_range(self, url,  macaroon, start, end):
        file_content= None
        command = self.get_base_command()
        if macaroon:
            command = command + ["-H", 'Authorization: Bearer '+macaroon]
        else:
            command = command + ["--cacert", self.proxy, "-E", self.proxy]
        command = command + ["-H", 'Range: bytes='+start+'-'+end]
        command = command + [url]
        
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if out.returncode ==0:
            file_content = stdout
        else:
           self.log.error("Something went wrong when executing command:\n" +self.get_command_str(command))
           self.log.debug("stdout:\n "+stdout)

        return file_content


    def put_file(self, url,  macaroon, filepath):
        file_content = None
        status = -1
        command = self.get_base_command()
        if macaroon:
            command = command + ["-H", 'Authorization: Bearer '+macaroon]
        else:
            command = command + ["--cacert", self.proxy, "-E", self.proxy]
        
        command = command + ["-T", filepath]
	command = command + [url]

        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if out.returncode == 0:
            status = 0
            if stdout != ":-)":
                self.log.error("file sent failed")
                self.log.error("stdout:\n "+stdout)
                self.log.error("executing command:\n" +self.get_command_str(command))
            else:
                self.log.info("file sent")
                self.log.debug("stdout:\n "+stdout)
        else:
           self.log.error("Something went wrong when executing command:\n" +self.get_command_str(command))
           self.log.debug("stdout:\n "+stdout)

    def get_file(self, url,  macaroon, new_filename=None):
        file_content = None
        status = -1
        command = self.get_base_command()
        if macaroon:
            command = command + ["-H", 'Authorization: Bearer '+macaroon]
        else:
            command = command + ["--cacert", self.proxy, "-E", self.proxy]
        
	command = command + [url]
        # If new_file is not set the content of the file is displayed instead
        if(new_filename is not None):
            command = command + ["-o", new_filename]

        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if out.returncode == 0:
            status = 0
            if(new_filename is None):
                self.log.info("file content\n: "+stdout)
            else:
                self.log.info("file was downladed: "+new_filename)
        else:
           self.log.error("Something went wrong when executing command:\n" +self.get_command_str(command))
           self.log.debug("stdout:\n "+stdout)
   
 
    def get_adler32(self, url, macaroon):
        command = self.get_base_command()
        command = command + ["-I", "-H", 'Want-Digest: adler32']
        if not macaroon:
            command = command + ["--cacert", self.proxy, "-E", self.proxy]
        else:
            command = command + ["-H", 'Authorization: Bearer '+macaroon]
        command = command + [url]
        
	self.log.debug(self.get_command_str(command))
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if out.returncode == 0:
            adler32 = self.extract_adler32(stdout)
        else:
           self.log.error("Something went wrong when executing command:\n" +self.get_command_str(command))
    
        return adler32
    
    def extract_adler32(self, response):
        adler32 = None
        self.log.debug("response: "+response)
        for line in response.split("\n"):
            if "Digest" in line:
                adler32 = line.split("=")[1]
        return adler32 
    
    def execute_cmd(self, cmd):
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line 
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def tpc(self, url_src, macaroon_src, url_dst, macaroon_dst):
        ret = -1
        command = self.get_base_command()
        command = command + ["-X", "COPY"]
        command = command + ["-H", 'TransferHeaderAuthorization: Bearer '+macaroon_src]
        command = command + ["-H", 'Source: '+url_src]
        command = command + ["-H", 'Authorization: Bearer '+macaroon_dst]
        command = command + [url_dst]
        out = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        self.log.debug("stdout:\n "+stdout)
        if out.returncode == 0:
            self.log.info("TPC OK")
            ret = 0
        else:
           self.log.error("Something went wrong when executing command:\n" +self.get_command_str(command))
        
        return ret

