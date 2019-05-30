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
def EmiratesSkyPostEvent(event):
    if(event.find("Delivered") != -1):
        return ("DLV", "Delivered")
    elif(event.find("Received from Flight") != -1):
        return ("RCF", "Received from Flight")
    elif(event.find("Document Delivered") != -1):
        return ('DDC', "Document Delivered")
    elif(event.find("Arrived") != -1):
        return ('ARR', "Arrived")
    elif(event.find("Departed") != -1):
        return ('DEP', "Departed")
    elif(event.find("Manifested") != -1):
        return ("MAN", "Manifested")
    elif(event.find("Booking Confirmed") != -1):
        return ('BKG', "Booking Confirmed")
    elif(event.find("Received from Shipper") != -1):
        return ('RCS', "Received from Shipper")
    return (None, None)

def EmiratesSkyPost(step):
    with open(step) as json_file:  
        data = json.load(json_file)
    postJson = copy.deepcopy(baseInfo.shipmentEventBase)
    postJson["unitID"]=data.get("Waybill")
    postJson["location"]=data.get("Station")
    postJson["eventTime"]=data.get("Status Date")
    postJson["eventName"], postJson["eventCode"]=EmiratesSkyPostEvent(data.get("Status"))
    postJson["notes"]=data["Flight Details"]
    #postJson["weight"] = data.get("Weight")
    #postJson["quantity"] = data.get("Pieces")
    #postJson["volume"]=data.get("Volume")
    if(postJson["eventCode"] == None):
        return
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
            EmiratesSkyPost(step)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])