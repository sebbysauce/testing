import json
import csv
import requests
import datetime
import schedule
import time
from config import params
from math import pow
from utilities import dprint, get_path
import pandas as pd


def discord(data):
    try:
        req = requests.post(params["discordChannel"], data=json.dumps(data),
                            headers={"Content-Type": "application/json"})
        req.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        print(data)


def checkSales():
    print("running checkSalesListing function")
    collection = params['collection']
    address = params['address']

    # url0 = "https://api.opensea.io/api/v1/assets"
    # querystring = {"order_direction": "desc", "collection": collection, "limit": "1", "offset": "0"}
    # response = requests.request("GET", url0, params=querystring)
    # res0 = json.loads(response.text)
    # address = res0["assets"][0]["asset_contract"]["address"]

    database = pd.read_csv(get_path("database.csv"), sep=',')
    salesTimestamp = str(database.iloc[0]["sales"])
    listingTimestamp = str(database.iloc[0]["listings"])

    ###### SALES ######
    url = "https://api.opensea.io/api/v1/events"
    querystring = {"occurred_after": salesTimestamp, "asset_contract_address": address,
                   "only_opensea": "false", "offset": "0", "event_type": "successful"}
    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    sales = result['asset_events']

    sales = sales[::-1]

    dprint(f'new sales - {len(sales)}')

    # data = {"embeds": [
    #     {
    #         "title": "Running sales and listing check",
    #         "color": 15258703,
    #         "fields": [
    #             {
    #                 "name": "Length",
    #                 "value": f"{str(len(sales))}",
    #                 "inline": True
    #             },
    #         ]
    #     }
    # ]}
    #
    # discord(data)

    for event in sales:
        # dprint(event)
        dprint(event["event_type"])

        title = "New Sale"
        tp = float(event['total_price'])
        color = 12342342
        token_id = str(event['asset']['token_id'])
        image = event['asset']['image_url']
        link = event['asset']['permalink']
        price = tp / pow(10, 18)
        creTime = event['created_date']

        formatTime = datetime.datetime.strptime(creTime, '%Y-%m-%dT%H:%M:%S.%f')
        timeStampTime = formatTime.replace(tzinfo=datetime.timezone.utc).timestamp()
        stringTime = formatTime.strftime('%d/%m/%Y, %H:%M:%S')

        dprint(timeStampTime)

        if timeStampTime > float(salesTimestamp):
            salesTimestamp = timeStampTime
            dprint("Sending the alert")
            data = {
                "username": "Father Panda bot",
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

    ###### LISTING ######

    url = "https://api.opensea.io/api/v1/events"
    querystring = {"occurred_after": listingTimestamp, "asset_contract_address": address,
                   "only_opensea": "false", "offset": "0", "event_type": "created"}
    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)
    listings = result['asset_events']

    listings = listings[::-1]

    dprint(f'new listing - {len(listings)}')

    for event in listings:
        # dprint(event)
        dprint(event["event_type"])

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

        if timeStampTime > float(listingTimestamp):
            listingTimestamp = timeStampTime
            dprint("Sending the alert")
            data = {
                "username": "Father Panda bot",
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

    with open(get_path('database.csv'), 'w') as csvfile:
        new_database = [{
            "sales": str(salesTimestamp),
            "listings": str(listingTimestamp)
        }]
        writer = csv.DictWriter(csvfile, fieldnames=["sales", "listings"])
        writer.writeheader()
        writer.writerows(new_database)


schedule.every(45).seconds.do(checkSales)

while True:
    schedule.run_pending()
    time.sleep(1)
