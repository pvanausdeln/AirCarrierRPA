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

def SingaporeEvent(event):
    if(event.find("Shipment Received") != -1):
        return ('RCS', "Received from Shipper")
    elif(event.find("Freight on Hand") != -1):
        return ('FOH', "Freight On Hand")
    elif(event.find("Cleared By Customs") != -1):
        return ('CCD', "Cleared by Customs")
    elif(event.find("Flight Departed") != -1):
        return ('DEP', "Departed")
    elif(event.find("Flight Arrived") != -1):
        return ('ARR', "Arrived")
    elif(event.find("Shipment Ready for Pick-up") != -1):
        return ("NFD", "Consignee/Agent notified of arrival")
    elif(event.find("Shipment Delivered") != -1):
        return ('DLV', "Shipment Delivered")
    elif(event.find("Shipment Checked Into Warehouse") != -1):
        return ('CIN', "Checked In")
    elif(event.find("Found Cargo") != -1):
        return ("FCA", "Found Cargo")
    elif(event.find("Temperature Log") != -1):
        return ('TEM', "Temperature Log")
    return (None, None)

def SingaporePost(step):
    with open(step) as json_file:  
        data = json.load(json_file)
    postJson = copy.deepcopy(baseInfo.shipmentEventBase)
    postJson["resolvedEventSource"] = "Singapore RPA"
    postJson["reportSource"] = "AirEvent"
    postJson["workOrderNumber"] = data.get("Work Order")
    postJson["shipmentReferenceNumber"] = data.get("Reference Number")
    postJson["unitId"] = data.get("Waybill")
    postJson["location"] = data.get("Station")
    postJson["eventCode"], postJson["eventName"] = SingaporeEvent(data.get("Status"))
    postJson["carrierName"] = data.get("Air Carrier")
    postJson["vessel"] = data.get("Flight Number")
    postJson["notes"] = data.get("Details")
    #try:
    #    postJson["Weight"] = data.get("Weight")
    #    postJson["Pieces"] = data.get("Pieces")
    #except:
    #    pass
    if(postJson["eventCode"] == None):
        return
    dt = datetime.datetime.strptime(data.get("Date") + " " + data.get("Time"), "%d %b %Y %H:%M")
    postJson["eventTime"] = dt.strftime('%m-%d-%Y %H:%M:%S')
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
        SingaporePost(step)

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
            SingaporePost(step)

if __name__ == "__main__":
    #testMain(sys.argv[1])
    main(sys.argv[1], sys.argv[2])