# *** Python3 Script to Call a Salesforce REST API using a JWT Token ****
# *** Author: Stephen Hawthorne ***
# *** Created: June 21, 2023 ***
# *** All Rights Reserved ***

# Imports
import auth
import requests

auth.doAuth()

token = auth.access_token
instance = auth.instance_url
object = 'Account'
recordId = '001Dn00000Gi7HJIAZ'
fields = 'Name,AccountNumber'

url = instance + '/services/data/v58.0/sobjects/Account/001Dn00000Gi7HJIAZ?fields=Name,AccountNumber'

r = requests.get(url, headers = {"Authorization":"Bearer " + token})
print(r.json())

AccountId = r.json()['Id']
AccountNum = r.json()['AccountNumber']
AccountName = r.json()['Name']

print('Account Id = ' + AccountId)
print('Account Number = ' + AccountNum)
print('Account Name = ' + AccountName)