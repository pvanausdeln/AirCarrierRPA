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

def AirBridgeEvent(event):
    if(event.find("Delivered") != -1):
        return ("DLV", "Delivered")
    elif(event.find("Received From Flight") != -1):
        return ("RCF", "Received from Flight")
    elif(event.find("Consignee/Agent notified of arrival") != -1):
        return ("NFD", "Consignee/Agent notified of arrival")
    elif(event.find("Arrival documents delivered to Consignee/Agent") != -1):
        return ("DDC", "Arrival documents delivered to consignee/agent")
    elif(event.find("Arrived") != -1):
        return ('ARR', "Arrived")
    elif(event.find("Departed on Flight") != -1):
        return ('DEP', "Departed on Flight")
    elif(event.find("Received From Shipper") != -1):
        return ('RCS', "Received from Shipper")
    elif(event.find("Cleared by Customs") != -1):
        return ('CBC', "Cleared by Customs")
    elif(event.find("Reported to Customs") != -1):
        return ('RTC', "Reported to Customs")
    return (None, None)

def AirBridgePost(step):
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
    postJson["eventCode"], postJson["eventName"] = AirBridgeEvent(data.get("Status"))
    postJson["carrierName"] = data.get("Air Carrier")
    if(postJson["eventCode"] == None):
        return
    data["EventTime"] = ''.join(x for x in data["EventTime"] if x in string.printable)
    postJson["eventTime"] = datetime.datetime.strptime(data.get("EventTime").title(), '%d%b%y%H:%M').strftime('%m-%d-%Y %H:%M:%S')
    print(json.dumps(postJson))
    #postJson["weight"] = data.get("Weight")
    #postJson["quantity"] = data.get("Pieces")
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
        AirBridgePost(step)

def main(containerList, cwd): #real main
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
            AirBridgePost(step)

if __name__ == "__main__":
    #testMain(sys.argv[1])
    main(sys.argv[1], sys.argv[2])