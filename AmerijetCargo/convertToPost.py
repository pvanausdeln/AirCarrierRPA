import sys
import os
import requests
import json
import copy
import datetime
import glob
import string

class baseInfo:
    postURL = "https://demo-api.iasdispatchmanager.com:8502/v1/bv/shipmentevents"

    shipmentEventBase = {
    "associatedAssetSize": None,
    "associatedUnitId": None,
    "billOfLadingNumber": None,
    "bookingNumber": None,
    "bookingOffice": None,
    "carrierCode": None,
    "carrierName": None,
    "city": None,
    "codeType": None,
    "consigneeName": None,
    "containerBookingNumber": None,
    "country": None,
    "createdBy": None,
    "customerOrderReferenceNumber": None,
    "destinationCity": None,
    "destinationSPLC": None,
    "destinationState": None,
    "eventCode": None,
    "eventName": None,
    "eventTime": None,
    "houseBill": None,
    "importReferenceNumber": None,
    "latitude": 0,
    "location": None,
    "longitude": 0,
    "masterBill": None,
    "notes": None,
    "onHandNumber": None,
    "originSPLC": None,
    "originatorCode": None,
    "originatorId": 0,
    "originatorName": None,
    "postalCode": None,
    "purchaseOrderReferenceNumber": None,
    "railBillingNumber": None,
    "reasonCode": None,
    "reasonName": None,
    "receiverCode": None,
    "receiverName": None,
    "reportSource": None,
    "reportedBy": None,
    "resolvedEventId": 0,
    "resolvedEventOriginalId": 0,
    "resolvedEventSource": None,
    "resolvedEventStatus": None,
    "sealNumber": None,
    "shipmentReferenceNumber": None,
    "signedBy": None,
    "state": None,
    "stopType": None,
    "terminalCode": None,
    "terminalFunction": None,
    "unitId": None,
    "unitSize": 0,
    "unitState": None,
    "unitTypeCode": None,
    "vessel": None,
    "voyageNumber": None,
    "workOrderNumber": None
    }
def AmerijetPostEvent(event):
    if(event.find("Customer Picked up Shipment") != -1):
        return ("DLV", "Customer Picked up Shipment")
    elif(event.find("Customer Picked Up Documents") != -1):
        return ("AWD", "Customer Picked Up Documents")
    elif(event.find("Customer was notified of Arrival") != -1):
        return ("NFD", "Customer was notified of Arrival")
    elif(event.find("Received Shipment") != -1):
        return ("RCF", "Received Shipment")
    elif(event.find("Departed") != -1):
        return ('DEP', "Departed")
    elif(event.find("Arrived at HUB") != -1):
        return ('RCS', "Arrived at HUB")
    elif(event.find("Reservation #") != -1):
        return ('BKD', "Reservation #")
    elif(event.find("Transferred/In Transit") != -1):
        return ('TFD', "Transferred/In Transit")
    elif(event.find("Released from Customs") != -1):
        return ('CCD', "Released from Customs")
    return (None, None)

def AmerijetPost(step):
    with open(step) as json_file:  
        data = json.load(json_file)
    postJson = copy.deepcopy(baseInfo.shipmentEventBase)
    postJson["resolvedEventSource"] = "AirBridge RPA"
    postJson["reportSource"] = "AirEvent"
    postJson["workOrderNumber"] = data.get("Work Order")
    postJson["shipmentReferenceNumber"] = data.get("Reference Number")
    postJson["unitId"] = data.get("Waybill")
    postJson["notes"] = ''.join(x for x in data.get("Description") if x in string.printable)
    postJson["location"] = data.get("Station")
    postJson["eventCode"], postJson["eventName"] = AmerijetPostEvent(data.get("Status")) #split the status accordingly to get the event name from it
    postJson["carrierName"] = data.get("Air Carrier")
    if(postJson["eventCode"] == None):
        return
    data["EventTime"] = ''.join(x for x in data["EventTime"] if x in string.printable)
    postJson["eventTime"] = data.get("Airbill Date")
    #postJson["quantity"] = data.get("Pieces")
    headers = {'content-type':'application/json'}
    r = requests.post(baseInfo.postURL, data = json.dumps(postJson), headers = headers, verify = False)
    print(json.dumps(postJson))
    print(r)
    return

def main(containerList, cwd):
    path=""
    for x in cwd.split("\\"):
        path+=x+"\\\\" #just to add escape sequences for the glob method to work fine
    for container in containerList:
        fileList = glob.glob(path + "ContainerInformation\\"+container+"Step*.json", recursive = True) #get all the json steps
        
        if (not fileList):
            continue
        fileList = [f for f in fileList if container in f] #set of steps for this number
        fileList.sort(key=os.path.getmtime) #order steps correctly (by file edit time)
        for step in fileList:
            AmerijetPost(step)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])