import os
import requests
import json

# url = 'http://127.0.0.1:8000/analytics_automated/submission/'
# r = requests.get(url)
# print(r.text)

# url = 'http://127.0.0.1:8000/analytics_automated/submission/32.json'
# r = requests.get(url)

url = 'http://127.0.0.1:8000/analytics_automated/submission/.json'
# payload = {'job': 'job1', 'submission_name': 'test', 'email': 'a@b.com'}
# r = requests.post(url, json=json.dumps(payload))

payload = {'input_data': ('input.txt', open('../static/files/file1.txt', 'rb'))}
data = {'job': 'job1', 'submission_name': 'test', 'email': 'daniel.buchan@ucl.ac.uk',
        'task1_all': True, 'task2_number': 12}
r = requests.post(url, data=data, files=payload)
print(r.text)
