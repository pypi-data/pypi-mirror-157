import requests
import os
from dotenv import load_dotenv

load_dotenv()
zabbix_auth_token = os.getenv('zabbix_auth_token') # used to connect to zabbix api

# TODO
## - create host (with agent)
## - create host (with snmp)
## - enable/disable host (status = 0 --> enable)
## - get enabled/disabled hosts (status = 0 --> enabled)
## - get all groupids
## - get a host interfaces
## - get all hosts in a groupid
## - get all templates


def welcome():
    print("Working!")
