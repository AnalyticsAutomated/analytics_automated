import os
import requests
import json

url = 'http://128.16.14.83/analytics_automated/submission/.json'
# url = 'http://127.0.0.1:8000/analytics_automated/submission/.json'

payload = {'input_data': ('prot.txt', open('../static/files/prot.txt', 'rb'))}
data = {'job': 'psipred',
        'submission_name': 'test',
        'email': 'daniel.buchan@ucl.ac.uk'}
r = requests.post(url, data=data, files=payload)
print(r.text)
