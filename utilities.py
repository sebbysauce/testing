from pprint import pprint
from config import params
import requests,json

def dprint(string):
    if params['development_mode']:
        pprint(string)

def discord(data):
    try:
        req = requests.post(params["discordChannel"], data=json.dumps(data),
                            headers={"Content-Type": "application/json"})
        req.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        print(data)