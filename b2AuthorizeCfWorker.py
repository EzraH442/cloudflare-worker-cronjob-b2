#!/bin/python3

import os
import requests
import base64
import json
import time
import schedule

flagDebug = True
env = os.environ["env"]

# Backblaze b2 settings
bucketSourceId = ""
b2AppKey = ""
b2AppKeyId = ""

# Cloudflare settings
cfAccountId = ""
cfWorkerApi = ""
cfWorkerName = ""

if env and env != "prod":
    with open("config.json") as config_file:
        config = json.loads(config_file.read())

    print("loaded config:")
    print(config)

    bucketSourceId = config["bucketSourceId"]
    b2AppKey = config["b2AppKey"]
    b2AppKeyId = config["b2AppKeyId"]
    cfAccountId = config["cfAccountId"]
    cfWorkerApi = config["cfWorkerApi"]
    cfWorkerName = config["cfWorkerName"]
else:
    flagDebug = True
    bucketSourceId = os.environ["bucketSourceId"]
    b2AppKey = os.environ["b2AppKey"]
    b2AppKeyId = os.environ["b2AppKeyId"]
    cfAccountId = os.environ["cfAccountId"]
    cfWorkerApi = os.environ["cfWorkerApi"]
    cfWorkerName = os.environ["cfWorkerName"]


def job():
    # An authorization token is valid for not more than 1 week
    # This sets it to the maximum time value
    maxSecondsAuthValid = 7 * 24 * 60 * 60  # one week in seconds

    # DO NOT CHANGE ANYTHING BELOW THIS LINE ###

    baseAuthorizationUrl = "https://api.backblazeb2.com/b2api/v2/b2_authorize_account"
    b2GetDownloadAuthApi = "/b2api/v2/b2_get_download_authorization"

    # Get fundamental authorization code

    idAndKey = b2AppKeyId + ":" + b2AppKey
    b2AuthKeyAndId = base64.b64encode(bytes(idAndKey, "utf-8"))
    basicAuthString = "Basic " + b2AuthKeyAndId.decode("UTF-8")
    authorizationHeaders = {"Authorization": basicAuthString}
    resp = requests.get(baseAuthorizationUrl, headers=authorizationHeaders)

    if flagDebug:
        print(resp.status_code)
        print(resp.headers)
        print(resp.content)

    respData = json.loads(resp.content.decode("UTF-8"))

    print(respData)

    bAuToken = respData["authorizationToken"]
    bFileDownloadUrl = respData["downloadUrl"]
    bPartSize = respData["recommendedPartSize"]
    bApiUrl = respData["apiUrl"]

    # Get specific download authorization

    getDownloadAuthorizationUrl = bApiUrl + b2GetDownloadAuthApi
    downloadAuthorizationHeaders = {"Authorization": bAuToken}

    resp2 = requests.post(
        getDownloadAuthorizationUrl,
        json={
            "bucketId": bucketSourceId,
            "fileNamePrefix": "",
            "validDurationInSeconds": maxSecondsAuthValid,
        },
        headers=downloadAuthorizationHeaders,
    )

    resp2Content = resp2.content.decode("UTF-8")
    resp2Data = json.loads(resp2Content)

    bDownAuToken = resp2Data["authorizationToken"]

    if flagDebug:
        print("authorizationToken: " + bDownAuToken)
        print("downloadUrl: " + bFileDownloadUrl)
        print("recommendedPartSize: " + str(bPartSize))
        print("apiUrl: " + bApiUrl)

    workerTemplate = ""
    with open("template.js", "r") as file:
        workerTemplate = file.read()

    workerCode = workerTemplate.replace("<B2_DOWNLOAD_TOKEN>", bDownAuToken)

    with open("code.js", "w") as file:
        file.write(workerCode)

    cfHeaders = {
        "Authorization": "Bearer " + cfWorkerApi,
        "Content-Type": "application/javascript",
    }

    cfUrl = (
        "https://api.cloudflare.com/client/v4/accounts/"
        + cfAccountId
        + "/workers/scripts/"
        + cfWorkerName
    )

    resp = requests.put(cfUrl, headers=cfHeaders, data=workerCode)

    if flagDebug:
        print(resp)
        print(resp.headers)
        print(resp.content)


schedule.every().day.at("00:00").do(job)

job()

while True:
    schedule.run_pending()
    time.sleep(60 * 60)  # wait one hour
