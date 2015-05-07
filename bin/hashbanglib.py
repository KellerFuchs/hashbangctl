import os
import sys
#import textwrap
from ConfigParser import ConfigParser
from provisor import Provisor
from provisor.utils import getch, validate_pubkey, drop_privileges

SUDO_USER = os.environ.get('SUDO_USER')
CONF_FILE = '/etc/hashbangctl.conf'

if not SUDO_USER:
    exit("This script is designed to be run with sudo")

if not os.path.isfile(CONF_FILE):
    exit("%s does not exist" % CONF_FILE)

config = ConfigParser()
config.read([CONF_FILE])

p = Provisor(
    uri=config.get('ldap','uri'),
    user=config.get('ldap','user'),
    password=config.get('ldap','password'),
    user_base=config.get('ldap','user-base'),
    group_base=config.get('ldap','group-base')
)

drop_privileges()

ldap_user = p.get_user(SUDO_USER)

user = {
    'name': ldap_user.setdefault('cn',['Unknown'])[0],
    'login': ldap_user['uid'][0],
    'uid': ldap_user['uidNumber'][0],
    'shell': ldap_user['loginShell'][0],
    'host': ldap_user['host'][0],
    'email': ldap_user['mailRoutingAddress'][0],
    'pubkeys': ldap_user['sshPublicKey'],
}

def ldap_sync():
    p.modify_user(
        SUDO_USER,
        pubkeys = user['pubkeys'],
        shell = user['shell'],
        name = user['name'],
    )
