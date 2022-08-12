import can
import time

## Defining Functions
def ThirdPartyId(DeviceId):
    message = can.Message(arbitration_id=0x000FDB81,data=[DeviceId%256, (DeviceId >> 8)%256], is_extended_id=True)
    print ("Handshake:\n")
    print ("Third Party Device Id: " + str(DeviceId) + "\n")
    return message

def StatusData(statusId, value):
    print ("Status Data:\n")
    print("Status ID: " + str(statusId) + " (" + str(hex(statusId)) + ")")
    print("Value: " + str(value) + " (" + str(hex(value)) + ")\n")
    message = can.Message(arbitration_id=0x000FDB80, data = [statusId%256, (statusId >> 8)%256, value%256, (value >> 8)%256, (value >> 16)%256, (value >> 24)%256], is_extended_id=True)
    return message

def PriorityStatusData(statusId, value):
    print ("Priority Status Data:\n")
    print("Status ID: " + str(statusId) + " (" + str(hex(statusId)) + ")")
    print("Value: " + str(value) + " (" + str(hex(value)) + ")\n")
    message = can.Message(arbitration_id=0x000FDB87, data = [statusId%256, (statusId >> 8)%256, value%256, (value >> 8)%256, (value >> 16)%256, (value >> 24)%256], is_extended_id=True)
    return message

def Validation(Call, Response):
    valid = Call.arbitration_id%256 == Response.data[0]
    return valid

def Handshake(DeviceId):
    Retry = True
    while Retry == True:
        message = ThirdPartyId(DeviceId)
        print("Sending...")
        print (message)
        print("Receiving...")
        response = can.Message(arbitration_id=0x000FDB02, data = [message.arbitration_id%256], is_extended_id=True)
        print (response)
        print()
        if response is None:
            Retry = True
            print("Retry 'Handshake'")
            time.sleep(1)
        else:
            ValidBool = Validation(message,response)
            if ValidBool == True:
                Retry = False
    return True

def SendStatusData(StatusId,Value):
    Retry = True
    while Retry == True:
        message = StatusData(StatusId, Value)
        print("Sending...")
        print (message)
        print("Receiving...")
        response = can.Message(arbitration_id=0x000FDB02, data = [message.arbitration_id%256], is_extended_id=True)
        print (response)
        if response is None:
            Retry = True
            print("Failed")
            time.sleep(5)
        else:
            ValidBool = Validation(message,response)
            if ValidBool == True:
                print("Success\n")
                Retry = False
                time.sleep(5)
            else:
                print("ValidationFail")
                Retry = True
    return True

def SendPriorityStatusData(StatusId,Value):
    Retry = True
    while Retry == True:
        message = PriorityStatusData(StatusId, Value)
        print("Sending...")
        print (message)
        print("Receiving...")
        response = can.Message(arbitration_id=0x000FDB02, data = [message.arbitration_id%256], is_extended_id=True)
        print (response)
        if response is None:
            Retry = True
            print("Failed")
            time.sleep(5)
        else:
            ValidBool = Validation(message,response)
            if ValidBool == True:
                print("Success\n")
                Retry = False
                time.sleep(10)
            else:
                print("ValidationFail")
                Retry = True
    return True

if __name__ == "__main__":
    DeviceId = 4108
    Handshake(DeviceId)
    