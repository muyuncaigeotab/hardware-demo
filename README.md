# hardware-demo

This repo is intended to provide integrators with a better understanding of GEOTAB's add-on protocols. Each folder in the repo is dedicated to a different protocol, with each containing a program version that can be used with hardware and another which is purely demonstrative. Regardless of the version being used, by running these programs, integrators will be able to observe the bytes and byte order required to send various types of messages to GEOTAB devices.

# Program configuration

Before running the hardware programs, the COM port number will need to be updated to reflect the port that the external device is connected to. The device ID may also be updated if the integrator has been provided a value from the SOLENG department. Once this is done, there should be no need to make any other changes to the program.

# Device set up

In order to use the hardware programs to communicate directly with a GEOTAB device, it is necessary to use a compatible adapter. The repo should function properly with most usb-can or usb-rs232 devices. These devices should be connected from the system running the program to the IOX of interest. The IOX must then be connected to the GEOTAB device, which is in turn connected to a powering three-wire harness.

Note that the repo relies on the python-can and pyserial libraries which are compatible with most basic adapters. If for some reason the device is not fit for use with these libraries, the program will not function as intended.

# Prompts

Whether a hardware or non-hardware program is being run, the user will be prompted to provide custom information (some protocols allow for more customization than others). This custom information is reflected in the program's output, demonstrating which bits can and cannot altered, as well as how they can be altered. This should make it easier to build and test custom integrations. 
