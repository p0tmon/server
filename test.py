
import requests
from random import random 

url = 'https://potmon-api.tdom.dev/log'
# url = 'https://potmon-api.tdom.dev/geo'

# x = requests.post(url, json=myobj)

for i in range(1):
    myobj = {'id': i, 'lon': 50 + random(), 'lat': -1.39 + random()}
    x = requests.post(url, json=myobj)
    print(x.text)

print("done")
