import IOXRS232_NoHardwareLib

# Contact Solutions Engineering to receive device Id for specific application
deviceId = 4204

IOXRS232_NoHardwareLib.handshake(deviceId)
IOXRS232_NoHardwareLib.requestDeviceData()
IOXRS232_NoHardwareLib.deviceDataAck()
IOXRS232_NoHardwareLib.sendStatusData()
IOXRS232_NoHardwareLib.sendPriorityStatusData()
IOXRS232_NoHardwareLib.sendPing()
IOXRS232_NoHardwareLib.sendCustomData()
IOXRS232_NoHardwareLib.sendMIMEData()
