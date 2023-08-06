import os
from dotenv import load_dotenv

load_dotenv()
zabbix_auth_token = os.getenv('zabbix_auth_token')

# TODO
### 


def add_one(number):
    return number + 1