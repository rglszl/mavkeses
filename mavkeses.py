import requests
import json
from flask import Flask
app = Flask(__name__)

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
    app.run()
    
