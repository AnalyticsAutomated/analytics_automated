import os
import requests
import json

url = 'http://bioinf.cs.ucl.ac.uk/psipred/api/submission.json'

payload = {'input_data': ('prot.txt', open('../submissions/files/prot.txt', 'rb'))}
data = {'job': 'disopred',
        'submission_name': 'testing',
        'email': 'daniel.buchan@ucl.ac.uk', }
r = requests.post(url, data=data, files=payload)
print(r.text)

#NOTE: Once posted you will need to use the GET submission endpoint
#to retrieve your results. Polling the server about once every 2 or 5 mins
#should be sufficient.
#
# Full details at http://bioinf.cs.ucl.ac.uk/web_servers/web_services/
