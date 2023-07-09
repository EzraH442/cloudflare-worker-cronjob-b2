#!/bin/python3

import requests
import base64
import json

flagDebug = True

with open('config.json') as config_file:
    config_json = json.loads(config_file.read())

print("loaded config:")
print(config_json)
# Backblaze b2 settings
bucketSourceId = config_json['bucketSourceId']
bucketFilenamePrefix = config_json['bucketFilenamePrefix']
b2AppKey = config_json['b2AppKey']
b2AppKeyId = config_json['b2AppKeyId']

# Cloudflare settings
cfAccountId = config_json['cfAccountId']
cfWorkerApi = config_json['cfWorkerApi']
cfWorkerName = config_json['cfWorkerName']

# An authorization token is valid for not more than 1 week
# This sets it to the maximum time value
maxSecondsAuthValid = 7*24*60*60 # one week in seconds

# DO NOT CHANGE ANYTHING BELOW THIS LINE ###

baseAuthorizationUrl = 'https://api.backblazeb2.com/b2api/v2/b2_authorize_account'
b2GetDownloadAuthApi = '/b2api/v2/b2_get_download_authorization'

# Get fundamental authorization code

idAndKey = b2AppKeyId + ':' + b2AppKey
b2AuthKeyAndId = base64.b64encode(bytes(idAndKey, 'utf-8'))
basicAuthString = 'Basic ' + b2AuthKeyAndId.decode('UTF-8')
authorizationHeaders = {'Authorization' : basicAuthString}
resp = requests.get(baseAuthorizationUrl, headers=authorizationHeaders)

if flagDebug:
    print (resp.status_code)
    print (resp.headers)
    print (resp.content)

respData = json.loads(resp.content.decode("UTF-8"))

bAuToken = respData["authorizationToken"]
bFileDownloadUrl = respData["downloadUrl"]
bPartSize = respData["recommendedPartSize"]
bApiUrl = respData["apiUrl"]

# Get specific download authorization

getDownloadAuthorizationUrl = bApiUrl + b2GetDownloadAuthApi
downloadAuthorizationHeaders = { 'Authorization' : bAuToken}

resp2 = requests.post(getDownloadAuthorizationUrl,
                      json = {'bucketId' : bucketSourceId,
                              'fileNamePrefix' : "",
                              'validDurationInSeconds' : maxSecondsAuthValid },
                      headers=downloadAuthorizationHeaders )

resp2Content = resp2.content.decode("UTF-8")
resp2Data = json.loads(resp2Content)

bDownAuToken = resp2Data["authorizationToken"]

if flagDebug:
    print("authorizationToken: " + bDownAuToken)
    print("downloadUrl: " + bFileDownloadUrl)
    print("recommendedPartSize: " + str(bPartSize))
    print("apiUrl: " + bApiUrl)


workerTemplate = ""
with open('template.js', 'r') as file:
    workerTemplate = file.read()

workerCode = workerTemplate.replace('<B2_DOWNLOAD_TOKEN>', bDownAuToken)

with open("code.js", 'w') as file:
    file.write(workerCode)

cfHeaders = { 'Authorization' : "Bearer " + cfWorkerApi,
              'Content-Type' : 'application/javascript' }

cfUrl = 'https://api.cloudflare.com/client/v4/accounts/' + cfAccountId + "/workers/scripts/" + cfWorkerName

resp = requests.put(cfUrl, headers=cfHeaders, data=workerCode)

if flagDebug:
    print(resp)
    print(resp.headers)
    print(resp.content)
