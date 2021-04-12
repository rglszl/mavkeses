import requests
import json


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
print("Átlagos késés: " + str(delaySum/numberOfTrains))
print("Max késés: " + str(maxDelay))
