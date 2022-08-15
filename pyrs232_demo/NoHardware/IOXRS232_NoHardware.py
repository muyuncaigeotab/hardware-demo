import IOXRS232_NoHardwareLib

# Contact Solutions Engineering to receive device Id for specific application
deviceId = 4204

# Contact Solutions Engineering to receive device Id for specific application
deviceId = 4204

# Sending Handshake
IOXRS232_NoHardwareLib.handshake(deviceId)

# Request Device Data
IOXRS232_NoHardwareLib.requestDeviceData()

# Device Data Acknowledgmenet
IOXRS232_NoHardwareLib.deviceDataAck()

# Sending Status Data
IOXRS232_NoHardwareLib.sendStatusData()

# Sending Priority Status Data
IOXRS232_NoHardwareLib.sendPriorityStatusData()

# Sending Ping
IOXRS232_NoHardwareLib.sendPing()

# Sending Custom Data
IOXRS232_NoHardwareLib.sendCustomData()

# Sending MIME Data
IOXRS232_NoHardwareLib.sendMIMEData()
