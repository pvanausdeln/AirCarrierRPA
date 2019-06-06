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

def ANANipponPostEvent(event):
    if(event.find("Shipment Booked") != -1):
        return ("BKD", "Shipment Booked")
    elif(event.find("Shipment Accepted") != -1):
        return ("RCS", "Received from Shipper")
    elif(event.find("Shipment Departed") != -1):
        return ("DEP", "Shipment Departed")
    elif(event.find("Freight on Hand") != -1):
        return ('FOH', "Freight on Hand")
    elif(event.find("Shipment Manifested") != -1):
        return ('MAN', "Manifested")
    #elif(event.find("Predeclaration") != -1):
    #    return ('PRD', "Predeclaration")
    #elif(event.find("Matching Cancelled") != -1):
    #    return ('MHC', "Matching Cancelled")
    elif(event.find("Flight Arrived") != -1):
        return ('ARR', "Arrived")
    elif(event.find("Shipment Arrived") != -1):
        return ('RCF', "Received from Flight")
    #elif(event.find("Carry-in is in progress") != -1):
    #    return ('CAR', "Carry-in is in progress")
    #elif(event.find("documentation check is done") != -1):
    #    return ('DCD', "Documentation check is done")
    #elif(event.find("Matched") != -1):
    #    return ('MHD', "Matched")
    elif(event.find("Customs Cleared") != -1):
        return ('CCD', "Customs Cleared")
    elif(event.find("Shipment Notified for Delivery") != -1):
        return ('NFD', "Consignee/Agent Notified")
    elif(event.find("Shipment Delivered") != -1):
        return ('DLV', "Shipment Delivered")
    #elif(event.find("Transhipment Accepted") != -1):
    #    return ('TFD', "Transhipment Accepted")
    return (None, None)

def ANANipponPost(step):
    with open(step) as json_file:  
        data = json.load(json_file)
    postJson = copy.deepcopy(baseInfo.shipmentEventBase)
    postJson["resolvedEventSource"] = "ANANippon RPA"
    postJson["reportSource"] = "AirEvent"
    postJson["workOrderNumber"] = data.get("Work Order")
    postJson["shipmentReferenceNumber"] = data.get("Reference Number")
    postJson["unitId"] = data.get("Waybill")
    postJson["location"] = data.get("Event").split(" ")[-1]
    postJson["vessel"] = data.get("Other Info").split("|").strip()
    postJson["eventCode"], postJson["eventName"] = ANANipponPostEvent(data.get("Event").strip())
    postJson["carrierName"] = data.get("Air Carrier")
    if(postJson["eventCode"] == None):
        return
    dt = datetime.datetime.strptime(data.get("Datetime"), "%d-%m %Y | %H:%M")
    postJson["eventTime"] = dt.strftime('%m-%d-%Y %H:%M:%S')
    print(json.dumps(postJson))
    #postJson["weight"] = data.get("Pieces/Weight").split(" ")[-2]
    #postJson["quantity"] = data.get("Pieces/Weight").split(" ")[0]
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
        ANANipponPost(step)

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
            ANANipponPost(step)

if __name__ == "__main__":
    #testMain(sys.argv[1])
    main(sys.argv[1], sys.argv[2])