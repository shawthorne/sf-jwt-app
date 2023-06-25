# sf-jwt-app

<img src="https://drive.google.com/file/d/1oh4rAZKTo_q-rBgBZQW3B1wxmWhuWigu/" alt="JWT Logo" title="JWT Logo">

## Overview

Salesforce provides several methods to Authenticate against it’s various API’s. A common method used for Server to Server integration is the [OAuth 2.0 JWT Bearer Flow](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_jwt_flow.htm&type=5). This article provides detailed steps to build this flow in Python3. Of note, while this article provides complete details on how to build and execute this Authentication Flow, I don’t get into actually using an API beyond a simple test to ensure our token and connection work.

## Prerequisites

1. Access to a Salesforce Sandbox or Dev Org
2. The latest version of Python3 installed locally
3. Visual Studio Code installed

## Step By Step

### Create an x509 Certificate and Private Key

*See Reference # 1 for more detailed instructions if needed*

1. Open a terminal
2. Create a project directory - mkdir jwt
3. Change to the new directory - cd jwt
4. Generate a private key, and store it in a file called server.key
    
    *Change SomePassword to a unique password*
    
    ```bash
    openssl genrsa -des3 -passout pass:SomePassword -out server.pass.key 2048
    ```
    
5. Export the key file to a file named server.key
    
    ```bash
    openssl rsa -passin pass:SomePassword -in server.pass.key -out server.key
    ```
    
6. You will now have 2 files created, server.pass.key & server.key. You can delete server.pass.key as it’s no longer needed
7. Generate a certificate signing request using the server.key file. You will be prompted for attributes which you should complete, although the actual values matter little.
    
    ```bash
    openssl req -new -key server.key -out server.csr
    ```
    
8. Generate a self-signed digital certificate from the server.key and server.csr files
    
    ```bash
    openssl x509 -req -sha256 -days 365 -in server.csr -signkey server.key -out server.crt
    ```
    
9. At this point you should have 3 files:
    1. **server.key -** The private key. This is the file you will use in your app to sign your Token Request
    2. **server.crt -** The digital certification. You upload this file when you create the connected app required by the JWT bearer flow.
    3. server.csr - The certificate signing request, which you will not use.

### Create a Service Account (User) in Salesforce

1. Create a Profile (we will use the Salesforce Integration User License)
    1. Clone the Salesforce API Only System Integrations
    2. Name = Service API User
2. Create a Permission Set
    1. Name = Service API Permission Set
    2. License = Salesforce API Integration
    3. Edit the Object Settings and grant Read Access to Accounts
    4. Under Field Permissions, check Read Access for all fields
    5. Save the changes
3. Create a User
    1. Setup\Users
    2. New User
    3. First Name = API
    4. Last Name = User
    5. Email = your email
    6. Username = Something unique, like api.user@test.not
    7. User License = Salesforce Integration
    8. Profile = Service API User
    9. Active = checked
    10. Time Zone = your time zone
    11. Uncheck “Generate new password…”
    12. Click Save
    13. Assign the Service API Permission Set to the User

### Create a Connected App in Salesforce

1. Setup\App Manager
2. New Connected App
3. Connected App Name = API Test
4. API Name = API_Test
5. Contact Email = your email
6. Enable OAuth Settings = checked
7. Callback URL = [https://localhost](https://localhost/)
8. Use digital signatures
    1. Choose File
    2. Select server.crt from earlier step
9. Available OAuth Scopes
    1. Select - Manage user data via APIs (api)
    2. Select - Perform requests at any time (refresh_token, offline_access)
10. Click Save

## Grant the user access to the connected app

1. View the connected app, click Manage then Edit Policies
2. Change Permitted Users from All users may self-authorize to Admin approved users are pre-authorized and click Save
3. Scroll down to Profiles and click Manage Profiles
4. Add the Profile assigned to your API User (Service API User)

### Create a new Directory and Populate with Core Files

1. Create a new Directory (wherever you choose) named sf-jwt-app
2. Change to the new directory
3. Create a file for our app
    1. touch app.py
4. Create a new directory for our certificate - mkdir certs
5. Copy the server.key file generated earlier into the certs directory
6. Open Visual Studio Code
    1. code .

### Create a Virtual Environment

1. In Visual Studio Code, open the Command Pallet (Command Shift P)
2. Choose Python: Create Environment
3. Choose Venv
4. Choose the latest version of Python3 installed
5. Open a new Terminal and verify you are in the virtual environment

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/fb4bc525-f774-4431-ad93-2f9f2824e962/Untitled.png)

### Create a File and Populate our Environment Variables

1. Create a new File in the root
    1. name = .env
    2. Open the file in the editor
    3. Paste in this text
    
    ```
    KeyFile = 'certs/server.key'
    
    ClientId = ''
    
    UserName = ''
    
    Domain = ''
    ```
    
    1. Update the .env file with your attributes
        1. ClientId
            1. In Salesforce, view your API Test connected app
            2. Click Manage Consumer Details
            3. Copy the Consumer Key and paste after ClientId in the file (between the single quotes)
        2. UserName
            1. Copy the Salesforce username you created earlier and paste after UserName in the file (between the single quotes)
        3. Domain
            1. https://test.salesforce.com //for a Sandbox
            2. https://login.salesforce.com //for a Production or Developer org

## Install Dependencies

1. Open a new Terminal inside Visual Studio Code
2. Run each of these commands one after another
    1. pip3 install python-dotenv
    2. pip3 install pyjwt
    3. pip3 install requests
    4. pip3 install cryptography

## Create our Python Files

1. Create a new file in the root to hold our Authorization code
    1. Name = auth.py
    2. Open the file in the editor
    3. Paste in this code
    
    ```python
    # Imports
    from dotenv import load_dotenv # pip3 install python-dotenv
    from datetime import datetime
    import jwt # pip3 install pyjwt
    import time
    import requests # pip3 install requests
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
    ```
    
2. Add our Test code
    1. Open app.py
    2. Open the file in the editor
    3. Paste in this code
    4. Change the Account Id to an Account in your org. Make sure the record has an Account Number.
    
    ```python
    # Imports
    import auth
    import requests
    
    auth.doAuth()
    
    url = auth.instance_url + '/services/data/v58.0/sobjects/Account/001Dn00000Gi7HJIAZ?fields=Name,AccountNumber'
    
    r = requests.get(url, headers = {"Authorization":"Bearer " + auth.access_token})
    print(r.json())
    
    AccountId = r.json()['Id']
    AccountNum = r.json()['AccountNumber']
    AccountName = r.json()['Name']
    
    print('Account Id = ' + AccountId)
    print('Account Number = ' + AccountNum)
    print('Account Name = ' + AccountName)
    ```
    

## Test

1. Right click on app.py and click **Run Python File in Terminal**
2. If everything worked correctly, you should see something that looks like this in the open Terminal window:

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/34a60ff4-c3ef-4a12-916f-2ed1596fe3b8/Untitled.png)

## Next Steps

1. To use this against one of the Salesforce API’s
    1. Modify your Permission Set to include the correct permissions for your Service user
    2. Modify app.py and substitute the test code for your real code

## References

1. [Create a Private key and Self-Signed Digital Certificate](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_key_and_cert.htm)
2. [OAuth 2.0 JWT Bearer Flow](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_jwt_flow.htm&type=5)
3. [Why do we need the JSON Web Token (JWT) in the modern web?](https://medium.com/swlh/why-do-we-need-the-json-web-token-jwt-in-the-modern-web-8490a7284482)
4. GitHub repository containing the project files
