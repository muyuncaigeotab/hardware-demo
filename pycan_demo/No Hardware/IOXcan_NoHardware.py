import IOXcan_NoHardwareLib

# Defining device ID (may be editted)
DeviceId = 4108

# Performing initial handshake
IOXcan_NoHardwareLib.Handshake(DeviceId)

# Inputting Status ID and status data value
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
    # Sending status data
    IOXcan_NoHardwareLib.SendStatusData(StatusId,statusDataValue)
    # Sending priority status data
    IOXcan_NoHardwareLib.SendPriorityStatusData(StatusId,statusDataValue)
else:
    print("Too many failed attempts")
    print("Quitting...")
    