#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
  Use this script to make a text-to-speech call to a phone number using Voice API

  To use this script:
  1. Copy this script to a local directory <NEXMO_DIR>.
  2. In <NEXMO_DIR>, use python package manager (https:#pip.pypa.io/en/stable/installing/) to install:
        Python crypto:          pip install pycrypto
        Python Jose:            pip install python-jose
        Python Requests:        pip install requests
  3. Set the parameters between lines 23 and 34.
  4. Run the script:
                python voice_api_first_tts_call.py
 """

import json
import os,sys
import requests
from datetime import datetime
from base64 import urlsafe_b64encode
import os
import calendar
import urllib
import urllib2
from jose import jwt

"""
   Set the parameters to run this script
"""
nexmo_key = "";
nexmo_secret = "";

#Leave blank unless you have already created an application
application_id = ""
#If you add an application ID here, add the private key in a file with the
#same name as the application ID in  the same directory as this script.

#Add the phone number to call
if len(sys.argv) != 2:
    print '''Usage:\n\t%s phone''' % str(sys.argv[0])
    sys.exit()
phone = "%s" % str(sys.argv[1]).strip()
phone_number_to_call = "86%s" % phone

#And the phone number you are calling from
#This does not have to be a real phone number, just in the correct format
virtual_number = "441632960961"

"""
  The base URL for Nexmo endpoints.
"""
base_url = 'https://api.nexmo.com'
version = '/v1'
action = ''

"""
 Function to generate a JWT using the private key associated with an application.
"""
def generate_jwt(application_id="none", keyfile="application_secret_key.txt") :
        print("Opening keyfile " + keyfile)
        application_private_key = open(keyfile, 'r').read()
        # Add the unix time at UCT + 0
        d = datetime.utcnow()

        token_payload = {
                "iat": calendar.timegm(d.utctimetuple()),  # issued at
                "application_id": application_id,  # application id
                "jti": urlsafe_b64encode(os.urandom(64)).decode('utf-8')
        }

        # generate our token signed with this private key...
        return jwt.encode(
                claims=token_payload,
                key=application_private_key,
                algorithm='RS256')
"""
   If you have not already created an application, this requests creates one for you and stores
   the private key locally in a local file application_id.
"""
if not application_id:

        print ("Can't see an application, let's create one for you.")

        action = '/applications/?'

        headers = {
        "Content-type": "application/json"
        }

        params = {
                'api_key': nexmo_key,
                'api_secret': nexmo_secret,
                'name' : 'First Voice API Call',
                'type' : 'voice',
                'answer_url' : 'https://example.com/ncco',
                'event_url' : 'https://example.com/call_status'
        }

        print params
        url =  base_url + version + action
        data =  urllib.urlencode(params)
        request = urllib2.Request(url, data)
        request.add_header('Accept', 'application/json')
        try:
                response = urllib2.urlopen(request)
                data = response.read()
                if response.code == 201:
                        application = json.loads(data.decode('utf-8'))
                        print "Application " + application['name'] + " has an ID of:" + application['id']
                        print "Saving your private key to a local file."
                        application_id = application['id']
                        f = open(application['id'], 'w')
                        f.write(application['keys']['private_key'])
                        f.close()
                else:
                        print "HTTP Response: " + response.code
                        print data
        except urllib2.HTTPError  :
                print error
else:
        if not os.path.exists(application_id) :
                print ("Please add the private key for your application in a file named " + application_id + " in  the same directory as this script." )


"""
 Make a TTS Call to a phone number
"""
print ("Using application ID " + application_id + " to call " +  phone_number_to_call )

print ("Generate a JWT for  " + application_id )

jwt = generate_jwt(application_id, application_id)

print ("This JWT authenticates you when you make a request to one of our endpoints: \n  " + jwt )


action = '/calls'
#Add the JWT to the request headers
headers = {
"Content-type": "application/json",
"Authorization": "Bearer {0}".format(jwt)
}

payload = {
        "to":[{
                "type": "phone",
                "number": phone_number_to_call
        }],
        "from": {
                "type": "phone",
                "number": virtual_number
                },
        "answer_url": ["https://nexmo-community.github.io/ncco-examples/first_call_talk.json"]
}

print ("Use the following payload to make the Call: \n" + json.dumps(payload, indent=4, sort_keys=True) )

print ("answer_url is pointing to the webhook endpoint providing the NCCO that manages the Call." )

print ("And make the Call. " )

#Create the request
response = requests.post( base_url + version + action , data=json.dumps(payload), headers=headers)

if (response.status_code == 201):
        print ("The Call status is: " + response.content  )
else:
        print( "Error: " + str(response.status_code) + " " +    response.content)

