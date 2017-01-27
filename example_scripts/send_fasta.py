import os
import requests
import json

# url = 'http://128.16.14.83/analytics_automated/submission.json'
url = 'http://127.0.0.1:8000/analytics_automated/submission.json'

#payload = {'input_data': ('prot.txt', open('../submissions/files/prot.txt', 'rb'))}
payload = {'input_data': ('prot.txt', open('known_pdb.fasta', 'rb'))}
data = {'job': 'domserf',
        'submission_name': 'test',
        'email': 'daniel.buchan@ucl.ac.uk'}
r = requests.post(url, data=data, files=payload)
print(r.text)
