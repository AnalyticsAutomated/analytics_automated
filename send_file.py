import os
import requests
import json

url = 'http://127.0.0.1:8000/analytics_automated/submission/'

payload = {'job_name': 'job1', 'submission_name': 'test', 'email': 'a@b.com'}
r = requests.post(url, data=json.dumps(payload))
print(r.text)

# payload = {'input_data': ('input.txt', open('./static/files/file1.txt', 'rb')),
#            'job_name': 'job1', 'submission_name': 'test', 'email': 'a@b.com'}
# r = requests.post(url, files=payload)
#
# print(r.text)
