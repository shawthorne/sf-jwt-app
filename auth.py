# *** Python3 Script to Authenticate to Salesforce using a JWT Token ****
# *** Author: Stephen Hawthorne ***
# *** Created: June 21, 2023 ***
# *** All Rights Reserved ***

# Install Dependencies
# pip3 install python-dotenv
# pip3 install pyjwt
# pip3 install requests
# pip3 install cryptography

# Imports
from dotenv import load_dotenv
#from datetime import datetime
import jwt
import time
import requests
import json
import os

def doAuth():
    # Get environment variables from .env file
    load_dotenv()
    KEY_FILE = os.getenv('KeyFile')
    ISSUER = os.getenv('ClientId')
    SUBJECT = os.getenv('UserName')
    DOMAIN = os.getenv('Domain')

    # Load the Private Key from the .key File
    print('Loading Private Key...')
    with open(KEY_FILE) as kf:
        private_key = kf.read()

    # Create the Claim
    print('Creating Claim...')
    claim = {
        'iss': ISSUER,
        'sub': SUBJECT,
        'aud': '{}'.format(DOMAIN),
        'exp': int(time.time()) + 300
    }

    # Create the Assertion
    print('Generating Signed JWT Assertion...')
    assertion = jwt.encode(claim, private_key, algorithm='RS256', headers={'alg':'RS256'})

    # Request an Authorization Token
    print('Making OAuth request...')
    endpoint = '{}/services/oauth2/token'.format(DOMAIN)
    r = requests.post(endpoint, data = { 
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': assertion
    })

    # Print the Response
    print('Response...')
    print('Status', r.status_code)
    print(r.json())

    # Parse the Response and Store the Auth Information
    reply = json.loads(r.text)
    global access_token
    global instance_url
    access_token = reply['access_token']
    instance_url = reply['instance_url']