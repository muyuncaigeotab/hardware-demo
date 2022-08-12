import IOXcan_NoHardwareLib

DeviceId = 4108
IOXcan_NoHardwareLib.Handshake(DeviceId)
attempts = 0
while attempts < 5:
    try:
        StatusId = int(input("Please enter a status ID: "))
        print()
        attempts = 0
        break
    except:
        print("Please enter a valid status ID")
        attempts += 1

while attempts < 5:
    try:
        statusDataValue = int(input("Please enter a status data value: "))
        print()
        attempts = 0
        break
    except:
        print("Please enter a valid status data value")
        attempts += 1
        
if attempts != 5 :   
    IOXcan_NoHardwareLib.SendStatusData(StatusId,statusDataValue)
    IOXcan_NoHardwareLib.SendPriorityStatusData(StatusId,statusDataValue)
else:
    print("Too many failed attempts")
    print("Quitting...")
    