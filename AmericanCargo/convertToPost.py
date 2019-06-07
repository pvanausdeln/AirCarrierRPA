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
def AmericanCargoEvent(event):
    if(event.find("Delivered") != -1):
        return ("DLV", "Delivered")
    elif(event.find("On Hand") != -1):
        return ("FOH", "On Hand")
    elif(event.find("Flight Arrived") != -1):
        return ("ARR", "Flight Arrived")
    elif(event.find("Flight Departed") != -1):
        return ("DEP", "Flight Departed")
    elif(event.find("Dispatched") != -1):
        return ('DPD', "Dispatched")
    elif(event.find("Planned") != -1):
        return ('PLN', "Planned")
    elif(event.find("Received") != -1):
        return ('RCS', "Received")
    elif(event.find("Booked") != -1):
        return ('BKD', "Booked")
    elif(event.find("Offloaded") != -1):
        return ('DIS', "Offloaded")
    elif(event.find("Awaiting Customs Clearance") != -1):
        return ('CRC', "Reported to Customs")
    return (None, None)

def AmericanPost(step):
    with open(step) as json_file:  
        data = json.load(json_file)
    postJson = copy.deepcopy(baseInfo.shipmentEventBase)
    postJson["resolvedEventSource"] = "American RPA"
    postJson["reportSource"] = "AirEvent"
    postJson["workOrderNumber"] = data.get("Work Order")
    postJson["shipmentReferenceNumber"] = data.get("Reference Number")
    postJson["unitId"] = data.get("Waybill")
    postJson["eventCode"], postJson["eventName"] = AmericanCargoEvent(data.get("Status"))
    postJson["carrierName"] = data.get("Air Carrier")
    if(postJson["eventCode"] == None):
        return
    #postJson["eventTime"] = datetime.datetime.strptime(data.get("EventTime").title(), '%d%b%y%H:%M').strftime('%m-%d-%Y %H:%M:%S') Get time using data.get(details) by splitting it accordingly.
    #postJson["weight"] = data.get("Weight")
    #postJson["quantity"] = data.get("Pieces/Container")
    #postJson["vessel"]=data.get("Flight/Truck")
    headers = {'content-type':'application/json'}
    r = requests.post(baseInfo.postURL, data = json.dumps(postJson), headers = headers, verify = False)
    print(json.dumps(postJson))
    print(r)
    return

def testMain(container): #test main
    fileList = glob.glob(os.getcwd() + "\\ContainerInformation\\"+container+"Step*.json", recursive = True) #get all the json steps
    if (not fileList):
        return
    fileList = [f for f in fileList if container in f] #set of steps for this number
    fileList.sort(key=os.path.getmtime) #order steps correctly (by file edit time)
    for step in fileList:
        AmericanPost(step)

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
            AmericanPost(step)

if __name__ == "__main__":
    #testMain(sys.argv[1])
    main(sys.argv[1], sys.argv[2])