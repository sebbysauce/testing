import json
import csv
import requests
import datetime
import schedule
import time
from config import params
from math import pow
from utilities import dprint, discord
import pandas as pd

def checkSales():
    print("running checkSales")
    collection = params['collection']
    address = params['address']

    # url0 = "https://api.opensea.io/api/v1/assets"
    # querystring = {"order_direction": "desc", "collection": collection, "limit": "1", "offset": "0"}
    # response = requests.request("GET", url0, params=querystring)
    # res0 = json.loads(response.text)
    # address = res0["assets"][0]["asset_contract"]["address"]

    database = pd.read_csv("database.csv", sep=',')
    subTimestamp = str(database.iloc[0]["timestamp"])

    ###### SALES ######
    url = "https://api.opensea.io/api/v1/events"
    querystring = {"occurred_after": subTimestamp, "asset_contract_address": address,
                   "only_opensea": "false", "offset": "0", "event_type": ["successful", "created"]}
    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    events = result['asset_events']

    events = events[::-1]

    dprint(len(events))

    # data = {"embeds": [
    #     {
    #         "title": "Running sales and listing check",
    #         "color": 15258703,
    #         "fields": [
    #             {
    #                 "name": "Length",
    #                 "value": f"{str(len(events))}",
    #                 "inline": True
    #             },
    #         ]
    #     }
    # ]}
    #
    # discord(data)

    for event in events:
        # dprint(event)
        dprint(event["event_type"])

        if event["event_type"] == 'successful':
            title = "New Sale"
            tp = float(event['total_price'])
            color = 12342342
        else:
            title = "New Listing"
            tp = float(event['starting_price'])
            color = 15258703

        token_id = str(event['asset']['token_id'])
        image = event['asset']['image_url']
        link = event['asset']['permalink']
        price = tp / pow(10, 18)
        creTime = event['created_date']

        formatTime = datetime.datetime.strptime(creTime, '%Y-%m-%dT%H:%M:%S.%f')
        timeStampTime = formatTime.replace(tzinfo=datetime.timezone.utc).timestamp()
        stringTime = formatTime.strftime('%d/%m/%Y, %H:%M:%S')

        dprint(timeStampTime)

        if timeStampTime > float(subTimestamp):
            subTimestamp = timeStampTime
            dprint("Sending the alert")
            data = {
                "username": "Opensea bot",
                "embeds": [
                    {
                        "title": title,
                        "color": color,
                        "fields": [
                            {
                                "name": "Panda",
                                "value": f"[{token_id}]({link})",
                                "inline": True
                            },
                            {
                                "name": "Price",
                                "value": str(price)
                            },
                            {
                                "name": "When",
                                "value": f"{stringTime} UTC"
                            },
                        ],
                        "image": {
                            "url": image
                        },
                    }
                ]
            }

            discord(data)
            time.sleep(1)

    with open('database.csv', 'w') as csvfile:
        new_database = [{
            "timestamp": str(subTimestamp)
        }]
        writer = csv.DictWriter(csvfile, fieldnames=["timestamp"])
        writer.writeheader()
        writer.writerows(new_database)


schedule.every(30).seconds.do(checkSales)

while True:
    schedule.run_pending()
    time.sleep(1)
