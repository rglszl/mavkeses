#!/usr/bin/env python3
import json

import flask
from flask import jsonify, Response
from qovery_client.qovery import Qovery

# --- START INIT ---

app = flask.Flask(__name__)

# this file is not used while deployed on Qovery
configuration_file_path = '../.qovery/local_configuration.json'

# get database configuration from Qovery
qovery = Qovery(configuration_file_path=configuration_file_path)

def getData():
    url="http://vonatinfo.mav-start.hu/map.aspx/getData"
    headers={'Content-Type': 'application/json'}
    data='{"a":"TRAINS","jo":{"pre":true,"history":false,"id":false}}'

    jsondata = json.loads(requests.post(url, headers=headers, data=data).text)

    numberOfTrains=0
    delaySum=0
    maxDelay=0
    for i in jsondata["d"]["result"]["Trains"]["Train"]:
        for j in i:
            try:
                if maxDelay<int(i["@Delay"]):
                    maxDelay=int(i["@Delay"])
                delaySum=delaySum+int(i["@Delay"])
                numberOfTrains=numberOfTrains+1
            except:
                pass
    return maxDelay, delaySum/numberOfTrains


@app.route('/atlagos')
def atlagos():
    maxDelay, avgDelay = getData()
    return str(avgDelay)

@app.route('/max')
def max():
    maxDelay, avgDelay = getData()
    return str(maxDelay)


if __name__ == '__main__':
    print('Server is ready!')
    app.run(host='0.0.0.0', port=5000)
