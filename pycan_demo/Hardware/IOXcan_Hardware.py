import can
import IOXcan_HardwareLib

canbus = can.interface.Bus(channel="COM6", bustype='slcan', bitrate=500000)
DeviceId = 4108
IOXcan_HardwareLib.Handshake(canbus, DeviceId)

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
    IOXcan_HardwareLib.SendStatusData(canbus,StatusId,statusDataValue)
    IOXcan_HardwareLib.SendPriorityStatusData(canbus,StatusId,statusDataValue)
else:
    print("Too many failed attempts")
    print("Quitting...")