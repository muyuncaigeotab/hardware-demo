# This library is intended for use with IOX-RS232
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

def hexStringFormatter(b):
    return("'" + hex(b) + "'")

# Successful handshake is required prior to device communication. Returns TRUE if successful.
def handshake(deviceId):
    print("HANDSHAKE:\n")
    ACK_request = int(input("ACK request? 1/0: "))
    wrap = int(input("Apply binary data packet wrapping? 1/0: "))
    counter = 0
    while(counter < 3):
        # send sync char ['0x55']
        print("sending sync char")
        print("['0x55']")
        time.sleep(1)
        counter += 1
    print("GO device handshake request")
    handshakeRequest = createMessage(bytes([0x01, 0]))
    print([hex(b) for b in handshakeRequest])
    time.sleep(1)
    print("sending handshake response")
    handshakeResponse = createMessage(
        bytes([0x81, 4, deviceId % 256, (deviceId >> 8) % 256, ACK_request*2 + wrap, 0]))
    print([hex(b) for b in handshakeResponse])
    time.sleep(1)
    if(ACK_request == 1):
        print("GO device handshake ACK")
        thirdPartyDataACK = createMessage(bytes([0x02, 0]))
        print([hex(b) for b in thirdPartyDataACK])
        time.sleep(1)
    print()
    return True


# This is a request-response message. It can be issued by the External Device
# when it wishes to receive the Device Data Info Message (Message Type 0x21).
def requestDeviceData():
    print("REQUEST DEVICE DATA:\n")
    # sending request for device data
    requestDD = createMessage(bytes([0x85, 0]))
    print("sending device data request")
    print([hex(b) for b in requestDD])
    time.sleep(1)

    # reading device data from GO device
    print("GO device data (may vary)")
    print("""['0x2', '0x21', '0x34', '0xcb', '0xdc', '0x67', '0x26', '0xb5', '0xea', '0xef',
          '0x19', '0x46', '0x36', '0x81', '0xd0', '0x0', '0x0', '0x0', '0x2', '0x0', 
          '0x0', '0x0', '0xb', '0x2', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', 
          '0xb3', '0xd', '0x0', '0x0', '0xff', '0xff', '0xff', '0xff', '0x0', '0x0', 
          '0x0', '0x0', '0x47', '0x39', '0x55', '0x52', '0x4d', '0x57', '0x56', '0x5a', 
          '0x37', '0x4e', '0x53', '0x53', '0x70', '0x54', '0x3']""")
    time.sleep(1)
    print()
    


# Issued by the External Device on receipt of the GO Device Data message.
def deviceDataAck():
    print("DEVICE DATA ACK:\n")
    print("sending device data ACK")
    print([hex(b) for b in createMessage(bytes([0x84, 0]))])
    time.sleep(1)
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
            print("Attemped read 5 times without success (Returned)")
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
def sendStatusData():
    print("SEND STATUS DATA:\n")
    # sending status data message to GO device
    DataId = int(input("Enter status data ID (eg. 53 for outside temp): "))
    dataValue = int(input("Enter data value: "))
    dataMessage = createMessage(bytes([0x80, 6, DataId % 256, (
        DataId >> 8) % 256, dataValue % 256, (dataValue >> 8) % 256, 0, 0]))
    print("Sending status data message to GO device")
    print([hex(b) for b in dataMessage])
    time.sleep(1)

    # reading third-party data ack
    print("Reading third party data ACK")
    thirdPartyDataACK = createMessage(bytes([0x02, 0]))
    print([hex(b) for b in thirdPartyDataACK])
    time.sleep(1)
    print()


# Priority Status Data will be treated the same as the 0x80 Status Data message,
# but will also be logged using an Iridium modem connection if available.
def sendPriorityStatusData():
    print("SEND PRIORITY STATUS DATA:\n")
    # sending priority status data message to GO device
    DataId = int(input("Enter priority status data ID (eg. 53 for outside temp): "))
    dataValue = int(input("Enter data value: "))
    dataMessage = createMessage(bytes([0x87, 6, DataId % 256, (
        DataId >> 8) % 256, dataValue % 256, (dataValue >> 8) % 256, 0, 0]))
    print("Sending priority status data message to GO device")
    print([hex(b) for b in dataMessage])
    time.sleep(1)

    # reading third-party data ack
    print("Reading third party data ACK")
    thirdPartyDataACK = createMessage(bytes([0x02, 0]))
    print([hex(b) for b in thirdPartyDataACK])
    time.sleep(1)
    print()


# This message can be issued periodically to check that GO device is active. Go device will
# reply with Third-Party Data Ack (Msg Type 0x02). If not, begin handshake sync.
def sendPing():
    print("SEND PING:\n")
    # sending ping to GO device
    print("Sending ping to GO device")
    pingMessage = createMessage(bytes([0x89, 0]))
    print([hex(b) for b in pingMessage])
    time.sleep(1)

    # checking for GO device ACK
    print("Reading third party data ACK")
    thirdPartyDataACK = createMessage(bytes([0x02, 0]))
    print([hex(b) for b in thirdPartyDataACK])
    time.sleep(1)
    print()


# Also known as "Free Format Third-Party Data", issued by external device when it wants data
# saved on the GO device in free format (1 to 27 bytes), saved in MyGeotab as Custom Data.
# Note: data must be type: bytes
def sendCustomData():
    print("SEND CUSTOM DATA:\n")
    data: bytes = stringToBytes(input("Enter string to be represented in Byte form (27 bytes max): "))
    if len(data) > 27:
        print("Data size too large (greater than 27 bytes)")

    # sending custom data to GO device
    customMessage = createMessage(bytes([0x82, len(data)]) + data)
    print("Sending custom data to GO device")
    print([hex(b) for b in customMessage])

    # checking for GO device ACK
    print("Reading third party data ACK")
    thirdPartyDataACK = createMessage(bytes([0x02, 0]))
    print([hex(b) for b in thirdPartyDataACK])
    time.sleep(1)
    print()



# Contents of message will be ignored by GO device and sent to  server for processing. GO device
# responds with Binary Data Response (0x22). Step 1 of sending a MIME message, see sendMIMEData()
def sendBinaryData(data: bytes):
    # sending binary data packet to GO device
    print("Sending binary data packet to GO device")
    binaryData = createMessage(bytes([0x86, len(data)]) + data)
    print([hex(b) for b in binaryData])
    time.sleep(1)
    
    # checking for device ACK (Msg Type 0x22)
    print("Reading device ACK")
    binaryDataResponse = createMessage(bytes([0x04, 0x01]) + bytes(3))
    print([hex(b) for b in binaryDataResponse])
    time.sleep(1)
    
    


# Binary data payload must adhere to protocol understood by server (MIME data transfer protocol)
# MIME-type data is transferred from external device to the server. Accessible as MIME Type blob.
# Data can be sent using the SDK (typeName: TextMessage)
def sendMIMEData():
    print("SEND MIME DATA:\n")
    MIMEType = bytes(input("Please enter MIMEType (eg. image/jpeg): "), "utf-8")
    customPayload = int(input("Would you like to enter a custom byte payload? 1/0: "))
    if(customPayload):
        payload = stringToBytes(input("Input your custom message as a string: "))
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
        sendBinaryData(firstPacket)

        # Sending all other packets
        for j in range(1, len(packetArr)):
            packet = bytes([j%255]) + packetArr[j]
            sendBinaryData(packet)
    else:
        firstPacket = "['0x02', '0x86', [Message Body Length], " + \
        " ".join(map(hexStringFormatter, bytes([0, len(MIMEType)]))) + \
        " " + " ".join(map(hexStringFormatter, MIMEType)) + \
        ", [Payload Length], [Payload 1], [Checksum], '0x03']"
        print("Sending first payload")
        print(firstPacket)
        time.sleep(1)
        
        print("Reading device ACK")
        binaryDataResponse = createMessage(bytes([0x04, 0x01]) + bytes(3))
        print([hex(b) for b in binaryDataResponse])
        time.sleep(1)
        
        for k in range(2,5):
           packet = "['0x02', '0x86', [Message Body Length], " + \
            "".join(map(hexStringFormatter, bytes(([k%255])))) + ', [Payload ' +  \
            str(k) + "]" + ", [Checksum], '0x03']"
           print("Sending payload " + str(k))
           print(packet)
           time.sleep(1)
            
           print("Reading device ACK")
           binaryDataResponse = createMessage(bytes([0x04, 0x01]) + bytes(3))
           print([hex(b) for b in binaryDataResponse])
           time.sleep(1)
    