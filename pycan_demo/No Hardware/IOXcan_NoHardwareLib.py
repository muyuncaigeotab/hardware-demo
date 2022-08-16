import can
import time

## Defining Functions

# Third party ID (0x81) message generation
def ThirdPartyId(DeviceId):
    message = can.Message(arbitration_id=0x000FDB81,data=[DeviceId%256, (DeviceId >> 8)%256], is_extended_id=True)
    print ("Handshake:\n")
    print ("Third Party Device Id: " + str(DeviceId) + "\n")
    return message

# Status data (0x80) message generation
def StatusData(statusId, value):
    print ("Status Data:\n")
    print("Status ID: " + str(statusId) + " (" + str(hex(statusId)) + ")")
    print("Value: " + str(value) + " (" + str(hex(value)) + ")\n")
    message = can.Message(arbitration_id=0x000FDB80, data = [statusId%256, (statusId >> 8)%256, value%256, (value >> 8)%256, (value >> 16)%256, (value >> 24)%256], is_extended_id=True)
    return message

# Priority status data (0x87) message generation
def PriorityStatusData(statusId, value):
    print ("Priority Status Data:\n")
    print("Status ID: " + str(statusId) + " (" + str(hex(statusId)) + ")")
    print("Value: " + str(value) + " (" + str(hex(value)) + ")\n")
    message = can.Message(arbitration_id=0x000FDB87, data = [statusId%256, (statusId >> 8)%256, value%256, (value >> 8)%256, (value >> 16)%256, (value >> 24)%256], is_extended_id=True)
    return message

# Validating successful communication
def Validation(Call, Response):
    valid = Call.arbitration_id%256 == Response.data[0]
    return valid

# Sending handshake
def Handshake(DeviceId):
    Retry = True
    while Retry == True:
        # Generating message
        message = ThirdPartyId(DeviceId)
        print("Sending...")
        print (message)
        print("Receiving...")
        # Generating expected response
        response = can.Message(arbitration_id=0x000FDB02, data = [message.arbitration_id%256], is_extended_id=True)
        print (response)
        print()
        # Validating expected response (not required but outlines hardware functionality)
        if response is None:
            Retry = True
            print("Retry 'Handshake'")
            time.sleep(1)
        else:
            ValidBool = Validation(message,response)
            if ValidBool == True:
                Retry = False
    return True

# Sending status data
def SendStatusData(StatusId,Value):
    Retry = True
    while Retry == True:
        # Generating message
        message = StatusData(StatusId, Value)
        print("Sending...")
        print (message)
        print("Receiving...")
        # Generating expected response
        response = can.Message(arbitration_id=0x000FDB02, data = [message.arbitration_id%256], is_extended_id=True)
        print (response)
        # Validating expected response (not required but outlines hardware functionality)
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

# Sending priority status data
def SendPriorityStatusData(StatusId,Value):
    Retry = True
    while Retry == True:
        # Generating message
        message = PriorityStatusData(StatusId, Value)
        print("Sending...")
        print (message)
        print("Receiving...")
        # Generating expected response
        response = can.Message(arbitration_id=0x000FDB02, data = [message.arbitration_id%256], is_extended_id=True)
        print (response)
        # Validating expected response (not required but outlines hardware functionality)
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
    