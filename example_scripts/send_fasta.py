import os
import requests
import json

url = 'http://bioinf.cs.ucl.ac.uk/psipred_beta/api/submission.json'

payload = {'input_data': ('prot.txt', open('../submissions/files/prot.txt', 'rb'))}
data = {'job': 'disopred',
        'submission_name': 'testing',
        'email': 'daniel.buchan@ucl.ac.uk', }
r = requests.post(url, data=data, files=payload)
print(r.text)
