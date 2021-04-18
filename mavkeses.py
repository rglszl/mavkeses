from flask import Flask, render_template
import threading
import time
from datetime import datetime
import json
import requests
import mysql.connector
import os
import pytz



class backgroundTask:
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()
        
    def run(self):
        while(True):
            url="http://vonatinfo.mav-start.hu/map.aspx/getData"
            headers={'Content-Type': 'application/json'}
            data='{"a":"TRAINS","jo":{"pre":true,"history":false,"id":false}}'

            jsondata = json.loads(requests.post(url, headers=headers, data=data).text)

            numberOfTrainsGysev=0
            numberOfTrainsMav=0
            numberOfTrains=0
            delaySumGysev=0
            delaySumMav=0
            delaySum=0
            maxDelayGysev=0
            maxDelayMav=0
            maxDelay=0
            for i in jsondata["d"]["result"]["Trains"]["Train"]:
                for j in i:
                    try:
                        if maxDelay<int(i["@Delay"]):
                            maxDelay=int(i["@Delay"])
                        delaySum=delaySum+int(i["@Delay"])
                        numberOfTrains=numberOfTrains+1
                        
                        if i["@Menetvonal"] == "MAV":
                            if maxDelayMav<int(i["@Delay"]):
                                maxDelayMav=int(i["@Delay"])
                            delaySumMav=delaySumMav+int(i["@Delay"])
                            numberOfTrainsMav=numberOfTrainsMav+1
                        if i["@Menetvonal"] == "GYSEV":
                            if maxDelayGysev<int(i["@Delay"]):
                                maxDelayGysev=int(i["@Delay"])
                            delaySumGysev=delaySumGysev+int(i["@Delay"])
                            numberOfTrainsGysev=numberOfTrainsGysev+1
                        
                    except:
                        pass
                    
            mydb = mysql.connector.connect(
                    host=os.environ.get('QOVERY_DATABASE_KESESEK_HOST'),
                    user=os.environ.get('QOVERY_DATABASE_KESESEK_USERNAME'),
                    password=os.environ.get('QOVERY_DATABASE_KESESEK_PASSWORD'),
                    database=os.environ.get('QOVERY_DATABASE_KESESEK_NAME'),
                    buffered=True
                )
            cursor = mydb.cursor()
            insert_into_query = """
            INSERT INTO {} (timestamp, keses, max) VALUES ( UNIX_TIMESTAMP(CONVERT_TZ(LOCALTIME(), '+00:00', @@session.time_zone)), '%s', '%s' )
            """
            
            avgAll = round(delaySum/numberOfTrains, 2) if numberOfTrains>0 else 0
            avgMav = round(delaySumMav/numberOfTrainsMav, 2) if numberOfTrainsMav>0 else 0
            avgGysev = round(delaySumGysev/numberOfTrainsGysev, 2) if numberOfTrainsGysev>0 else 0
            
            cursor.execute(insert_into_query.format("minden"), (avgAll, maxDelay))
            cursor.execute(insert_into_query.format("mav"), (avgMav, maxDelayMav))
            cursor.execute(insert_into_query.format("gysev"), (avgGysev, maxDelayGysev))
            mydb.commit()

            
            time.sleep(300)
        
         

app = Flask(__name__)

@app.route('/keses')
def keses():
    mydb = mysql.connector.connect(
                    host=os.environ.get('QOVERY_DATABASE_KESESEK_HOST'),
                    user=os.environ.get('QOVERY_DATABASE_KESESEK_USERNAME'),
                    password=os.environ.get('QOVERY_DATABASE_KESESEK_PASSWORD'),
                    database=os.environ.get('QOVERY_DATABASE_KESESEK_NAME'),
                    buffered=True
        )
    cursor = mydb.cursor()
    cursor.execute("SELECT KESES, MAX, TIMESTAMP FROM minden ORDER BY TIMESTAMP DESC LIMIT 1")
    (avgAll, maxAll, ts) = cursor.fetchone()
    cursor.execute("SELECT KESES, MAX FROM mav ORDER BY TIMESTAMP DESC LIMIT 1")
    (avgMav, maxMav) = cursor.fetchone()
    cursor.execute("SELECT KESES, MAX FROM gysev ORDER BY TIMESTAMP DESC LIMIT 1")
    (avgGysev, maxGysev) = cursor.fetchone()
    return render_template("template.html", ts=datetime.fromtimestamp(int(ts), pytz.timezone("Europe/Budapest")).strftime('%Y-%m-%d %H:%M:%S'), avgAll=avgAll, maxAll=maxAll,avgMav=avgMav, maxMav=maxMav,avgGysev=avgGysev,maxGysev=maxGysev)
                   
def main():
    try:
        begin = backgroundTask()
    except:
        abort(500)
    app.run(host='0.0.0.0',threaded=True)

main()
