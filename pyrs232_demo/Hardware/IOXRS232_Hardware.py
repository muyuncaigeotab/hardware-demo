import serial
import IOXRS232_HardwareLib
from os.path import dirname, join

# Test image for additional testing
current_dir = dirname(__file__)
file_path = join(current_dir, "testImage.jpg")

comPort = "COM9"
# Contact Solutions Engineering to receive device Id for specific application
deviceId = 4205

# JPEG MIME type
mimeType = bytes("image/jpeg", "utf-8")

# JPEG image for MIME transfer
with open(file_path, 'rb') as f:
    content = f.read()
    b = bytearray(content)

# opening serial port, setting baud rate
with serial.Serial(port=comPort, baudrate=9600, timeout=10) as tester:
    while True:
        if(IOXRS232_HardwareLib.handshake(tester, deviceId)):
            break
        else:
            print("Handshake error, trying again...\n")
    print("Handshake Successful.\n")
    
    # requesting Device Data
    result = IOXRS232_HardwareLib.requestDeviceData(tester)
    print("Request Successful.\n") if result else print(
        "Request Failed.\n")
    
    IOXRS232_HardwareLib.deviceDataAck(tester)
    
    # sending Status Data (35251: External Air Temperature, 20C)
    result = IOXRS232_HardwareLib.sendStatusData(tester)
    print("Status Data sent.\n") if result else print(
        "Error occurred sending Status Data.\n")
    
    # sending Priority Status Data
    result = IOXRS232_HardwareLib.sendPriorityStatusData(tester)
    print("Priority Status Data sent.\n") if result else print(
        "Error occurred sending Priority Status Data.\n")
    
    # sending ping
    result = IOXRS232_HardwareLib.sendPing(tester)
    print("Ping sent.\n") if result else print(
        "Error occurred sending ping.\n")
    
    # sending Custom Data
    result = IOXRS232_HardwareLib.sendCustomData(tester)
    print("Custom Data sent.\n") if result else print(
        "Error occurred sending Custom Data.\n")

    # sending MIME Data
    result = IOXRS232_HardwareLib.sendMIMEData(tester)
    if result:
        print("MIME transfer successful.")
    else:
        print("MIME transfer unsuccessful.")

    # # XXX retrieving MIME Data from the server
    # message = iox_serial_2.readMimeMessage(tester)
    # print("MIME data recieved: ", message)