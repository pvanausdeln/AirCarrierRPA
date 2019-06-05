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

def LufthansaEvent(event):
    if(event.find("Booking confirmed") != -1):
        return ("BKD", "Shipment Booked")
    elif(event.find("Shipment accepted") != -1):
        return ('RCS', "Received from Shipper")
    elif(event.find("Departed") != -1):
        return ('DEP', "Departed")
    elif(event.find("Manifested") != -1):
        return ('MAN', "Manifested")
    elif(event.find("Arrived") != -1):
        return ('ARR', "Arrived")
    elif(event.find("Received from flight") != -1):
        return ("RCF", "Received from Flight")
    elif(event.find("Offload") != -1):
        return ("U", "Unloaded")
    elif(event.find("Ready for pick-up") != -1):
        return ('NFD', "Consignee/Agent notified of arrival")
    elif(event.find("Cargo Delivered") != -1):
        return ('DLV', "Delivered")
    elif(event.find("Customs") != -1):
        return ('ART', "Arrived at Terminal")
    
    return (None, None)

def LufthansaPost(step):
    with open(step) as json_file:  
        data = json.load(json_file)
    postJson = copy.deepcopy(baseInfo.shipmentEventBase)
    postJson["resolvedEventSource"] = "Lufthansa RPA"
    postJson["reportSource"] = "AirEvent"
    postJson["workOrderNumber"] = data.get("Work Order")
    postJson["shipmentReferenceNumber"] = data.get("Reference Number")
    postJson["unitId"] = data.get("Waybill")
    postJson["location"] = data.get("Station")
    postJson["eventCode"], postJson["eventName"] = LufthansaEvent(data.get("Description"))
    postJson["carrierName"] = data.get("Air Carrier")
    if(postJson["eventCode"] == None):
        return
    try:
        dt = datetime.datetime.strptime(data.get("Actual time").strip(), "%d %B %y / %H:%M")
        dt = dt.replace(year=datetime.datetime.now().year)
        if(dt.date() > datetime.datetime.today().date()):
            dt = dt.replace(year = datetime.datetime.year-1)
    except:
        return
    postJson["eventTime"] = dt.strftime('%m-%d-%Y %H:%M:%S')
    print(json.dumps(postJson))
    #postJson["weight"] = data.get("Actual\npieces / weight").split("/")[1].strip()
    #postJson["quantity"] = data.get("Actual\npieces / weight").split("/")[0].strip()
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
        LufthansaPost(step)

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
            LufthansaPost(step)

if __name__ == "__main__":
    testMain(sys.argv[1])
    #main(sys.argv[1], sys.argv[2])