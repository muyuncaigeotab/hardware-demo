# This library is intended for use with IOX-RS232
import re
import time


def checksum(message):  # Messages contain a 2-byte Fletcher’s Checksum. The checksum values are bytes, and as such overflow from 255 (0xFF) to 0 (0x00). Includes STX, LEN, and TYPE

    b0 = 0
    b1 = 0
    for i in range(0, len(message)):
        b0 += int(message[i])
        b1 += b0
    return bytes([b0 % 256, b1 % 256])


def createMessage(message):
    message = bytes([0x02]) + message
    check = checksum(message)
    message = message + check + bytes([0x03])
    return message


# This function is used to turn type str to type bytes (useful for Custom Data)
def stringToBytes(string):
    return bytes(string, 'utf-8')


# Successful handshake is required prior to device communication. Returns TRUE if successful.
def handshake(serialPort, deviceId):
    print("HANDSHAKE:\n")
    while(1):
        try:
            ACK_request = int(input("Please enter either a 1 or 0 for ACK request selection: "))
        except:
            print("input not valid\n")
        else:
            if(ACK_request == 1 or ACK_request == 0):
                print()
                break
            else:
                print("input not valid\n")
    while(1):
        try:
            wrap = int(input("Please enter either a 1 or 0 as a response for binary wrap selection: "))
        except:
            print("input not valid\n")
        else:
            if(wrap == 1 or wrap == 0):
                print()
                break
            else:
                print("input not valid\n")
    counter = 0
    while(1):
        # send sync char ['0x55']
        serialPort.write(bytes([0x55]))
        print("sending sync char")
        print("['0x55']\n")
        
        # checking for handshake request
        print("GO device handshake request")
        readback = serialPort.read(6)
        print([hex(b) for b in readback])
        counter += 1
        
        if len(readback) == 6 and readback[1] == 1:
            print()
            break
        elif counter > 9:
            print("Handshake failed 10 times")
            print("Returning...")
            return False
        print("Handshake failed, trying again...\n")  
        time.sleep(1)

    # sending handshake response
    print("sending handshake response")
    handshakeResponse = createMessage(
        bytes([0x81, 4, deviceId % 256, (deviceId >> 8) % 256, wrap*2 + ACK_request, 0]))
    serialPort.write(handshakeResponse)
    print([hex(b) for b in handshakeResponse])
    print()

    # checking for handshake ACK
    if(ACK_request == 1):
        print("GO device handshake ACK")
        readback = serialPort.read(6)
        print([hex(b) for b in readback])
        print()
        return True if (len(readback) == 6 and readback[1] == 2) else False
    else:
        return True


# This is a request-response message. It can be issued by the External Device
# when it wishes to receive the Device Data Info Message (Message Type 0x21).
def requestDeviceData(serialPort):
    print("REQUEST DEVICE DATA:\n")
    # sending request for device data
    print("sending device data request")
    requestDD = createMessage(bytes([0x85, 0]))
    serialPort.write(requestDD)
    print([hex(b) for b in requestDD])
    print()

    # reading device data from GO device
    print("GO device data")
    readback = serialPort.read(58)
    print([hex(b) for b in readback])
    print()
    return [hex(b) for b in readback] if readback[1] == 0x21 else False


# Issued by the External Device on receipt of the GO Device Data message.
def deviceDataAck(serialPort):
    print("DEVICE DATA ACK:\n")
    print("sending device data ACK")
    deviceDACK = createMessage(bytes([0x84, 0]))
    serialPort.write(deviceDACK)
    print([hex(b) for b in deviceDACK])
    print()


# Read binary packet TextMessage send from server to GO device via myGeotab SDK, returns message content.
# A packet size of 241 is used for the read as this is the size sent from server.
def readMimeMessage(serialPort):
    binaryMessage = bytes()
    # Begin reading binary data (timeout after 5 attempts), save packets in string binaryMessage
    for count in range(5):
        readback = serialPort.read(241)
        if(len(readback) > 0):
            break
        elif(count == 4):
            print("Attempted read 5 times without success (Returned)")
            return
    # ---FIRST PACKET---
    # Breaking down first packet. Contains information like MimeType and data length
    # Checking for message start (0x02), message type (0x23) and sequence number (0x00)
    if readback[0] == 0x02 and readback[1] == 0x23 and readback[3] == 0x00:
        # Each byte of readback is defined in HDK reference documentation
        mimeTypeLength = readback[4]
        mimeType = readback[5:5+mimeTypeLength]

        # b/c MIME first 5+ bytes reserved
        messageBodyLength = readback[2] - mimeTypeLength - 5
        index = 4 + mimeTypeLength  # points to last byte read

        # payload length is given in little endian notation, converting to int
        payloadLength = ""
        for b in readback[index+1: index+5]:
            payloadLength = str(hex(b))[2:4] + payloadLength
        payloadLength = int(payloadLength, 16)
        index += 4

        # write data in first packet to binaryMessage
        binaryMessage += readback[index + 1: index + messageBodyLength]

        # checksum check
        if(bytes(readback[-3:-1]) != checksum(readback[:-3])):
            print("Packet 0: Checksum error.")
            return
    else:
        print("Invalid packet wrapping.")
        return
    # ---REMAINING PACKETS---
    readback = serialPort.read(241)
    packetCount = 0
    # loop through remaining data packets, stitching them together in binaryMessage
    while len(readback) > 0:
        packetCount += 1 % 255
        # checking for proper wrapping
        if not readback[0] == 0x02 and readback[1] == 0x23:
            print("Inproper wrapping, Packet: ", packetCount)
            return
        # confirming sequence number
        elif readback[3] != packetCount:
            print("Sequence error, value: ",
                  readback[3], ", Expected: ", packetCount)
            return
        # checking checkSum
        elif bytes(bytes(readback[-3:-1]) != checksum(readback[:-3])):
            print("Packet ", packetCount, ": Checksum error.")
            return
        else:
            messageBodyLength = readback[2]
            binaryMessage += readback[4:3+messageBodyLength]
        # Grab next packet
        readback = serialPort.read(241)

    # Checking payload length for discrepancies
    if(payloadLength == len(binaryMessage)):
        return binaryMessage
    else:
        print("Payload length does not match expected value. Current: ",
              len(binaryMessage), " Expected: ", payloadLength)
        return

# ---------------------------- Third Party Data -------------------------------
# -----------------------------------------------------------------------------


# Sent by the external device whenever it requires Third-Party Data to be saved on the
# GO device as Status Data. (Note: DataId is assigned by Geotab)
def sendStatusData(serialPort):
    # sending status data message to GO device
    print("SEND STATUS DATA:\n")
    while(1):
        try:
            DataId = int(input("Enter status data ID (eg. 53 for outside temp): "))
        except:
            print("input not valid\n")
        else:
            if(DataId >= 0):
                print(hex(DataId), "\n")
                break
            else:
                print("Please enter a positive value\n")
        print()
    while(1):
        try:
            dataValue = int(input("Enter data value: "))
        except:
            print("input not valid\n")
        else:
            if(dataValue >= 0):
                print(hex(dataValue), "\n")
                break
            else:
                print("Please enter a positive value\n")
        print()
    # sending status data message to GO device
    dataMessage = createMessage(bytes([0x80, 6, DataId % 256, (
        DataId >> 8) % 256, dataValue % 256, (dataValue >> 8) % 256, 0, 0]))
    print("Sending status data message to GO device")
    serialPort.write(dataMessage)
    print([hex(b) for b in dataMessage])
    print()

    # reading third-party data ack
    readback = serialPort.read(6)
    print("Reading third party data ACK")
    print([hex(b) for b in readback])
    print()
    return True if len(readback) == 6 and readback[1] == 2 else False


# Priority Status Data will be treated the same as the 0x80 Status Data message,
# but will also be logged using an Iridium modem connection if available.
def sendPriorityStatusData(serialPort):
    print("SEND PRIORITY STATUS DATA:\n")
    # sending priority status data message to GO device
    while(1):
        try:
            DataId = int(input("Enter status data ID (eg. 53 for outside temp): "))
        except:
            print("input not valid\n")
        else:
            if(DataId >= 0):
                print(hex(DataId), "\n")
                break
            else:
                print("Please enter a positive value\n")
        print()
    while(1):
        try:
            dataValue = int(input("Enter data value: "))
        except:
            print("input not valid\n")
        else:
            if(dataValue >= 0):
                print(hex(dataValue), "\n")
                break
            else:
                print("Please enter a positive value\n")
        print()
    dataMessage = createMessage(bytes([0x87, 6, DataId % 256, (
        DataId >> 8) % 256, dataValue % 256, (dataValue >> 8) % 256, 0, 0]))
    print("Sending priority status data message to GO device")
    serialPort.write(dataMessage)
    print([hex(b) for b in dataMessage])
    print()

    # reading third-party data ack
    print("Reading third party data ACK")
    readback = serialPort.read(6)
    print([hex(b) for b in dataMessage])
    print()
    return True if len(readback) == 6 and readback[1] == 2 else False


# This message can be issued periodically to check that GO device is active. Go device will
# reply with Third-Party Data Ack (Msg Type 0x02). If not, begin handshake sync.
def sendPing(serialPort):
    print("SEND PING:\n")
    # sending ping to GO device
    print("Sending ping to GO device")
    pingMessage = createMessage(bytes([0x89, 0]))
    serialPort.write(pingMessage)
    print([hex(b) for b in pingMessage])
    print()

    # checking for GO device ACK
    print("Reading third party data ACK")
    readback = serialPort.read(6)
    print([hex(b) for b in readback])
    print()
    return True if len(readback) == 6 and readback[1] == 2 else False


# Also known as "Free Format Third-Party Data", issued by external device when it wants data
# saved on the GO device in free format (1 to 27 bytes), saved in MyGeotab as Custom Data.
# Note: data must be type: bytes
def sendCustomData(serialPort):
    print("SEND CUSTOM DATA:\n")
    while(1):
        data: bytes = stringToBytes(input("Enter string to be represented in Byte form (27 bytes max): "))
        if len(data) > 27:
            print("Data size too large (greater than 27 bytes)")
        else:
            print([hex(b) for b in data], "\n")
            break
    # sending custom data to GO device
    customMessage = createMessage(bytes([0x82, len(data)]) + data)
    serialPort.write(customMessage)
    print("Sending custom data to GO device")
    print([hex(b) for b in customMessage], "\n")

    # checking for GO device ACK
    print("Reading third party data ACK")
    readback = serialPort.read(6)
    print([hex(b) for b in readback])
    print()
    return True if len(readback) == 6 and readback[1] == 2 else False


# Contents of message will be ignored by GO device and sent to  server for processing. GO device
# responds with Binary Data Response (0x22). Step 1 of sending a MIME message, see sendMIMEData()
def sendBinaryData(serialPort, data: bytes):

    # sending binary data packet to GO device
    print("Sending binary data packet to GO device")
    binaryData = createMessage(bytes([0x86, len(data)]) + data)
    serialPort.write(binaryData)
    print([hex(b) for b in binaryData])
    print()

    # checking for device ACK (Msg Type 0x22)
    print("Reading device ACK")
    readback = serialPort.read(10)
    print([hex(b) for b in readback])
    print()
    if not len(readback) == 10 or not readback[1] == 34:  # 34 = 0x22
        print("\n\nError occurred reading ACK (Msg Type 0x22).")
        print([hex(b) for b in readback], "\n\n")
        return False
    elif readback[3] == 1:
        return True
    else:
        print("Binary transmission failure.")
        return False


# Binary data payload must adhere to protocol understood by server (MIME data transfer protocol)
# MIME-type data is transferred from external device to the server. Accessible as MIME Type blob.
# Data can be sent using the SDK (typeName: TextMessage)
def sendMIMEData(serialPort):
    print("SEND MIME DATA:")
    print("(May take over a minute)\n")
    MIMEType = bytes(input("Please enter MIMEType (eg. image/jpeg): "), "utf-8")
    print()
    payload = stringToBytes(input("Input your custom message as a string: "))
    print()
    firstLen = 244-len(MIMEType)  # first packet data length
    packetArr = [payload[0:firstLen]]
    packetCount = 0
    # Moving each packet's data into its own array element (250 bytes each)
    for i in range(int((len(payload)-firstLen)/249)):
        packetArr.append(payload[firstLen + i*249: firstLen + (i+1)*249])
        packetCount += 1
    # Final packet of data
    packetArr.append(payload[(firstLen+packetCount*249):])
    
    # First packet sent, contains the MIME type and payload length
    firstPacket = bytes([0, len(MIMEType)]) + MIMEType + \
        (len(payload)).to_bytes(4, "little") + \
        packetArr[0]  # little endian notation
    sentData = sendBinaryData(serialPort, firstPacket)
    if not sentData:
        return False
    
    # Sending all other packets
    for j in range(1, len(packetArr)):
        packet = bytes([j%255]) + packetArr[j]
        sentData = sendBinaryData(serialPort, packet)
        if not sentData:
            print("Fault occurred: Packet ", j+1)
            return False
        
    # Looking for device response (response changes based on handshake config)
    print("Reading MIMEType ACK")
    readback = serialPort.readline()
    print([hex(b) for b in readback])
    print()
    
    if readback[1] == 35 or readback[1] == 3: # 35 = 0x23, 3 = 0x3
        return True
    else:
        return False
