# Information obtained from StellarNet
# Written by Daniel Cote at http://www.dcclab.ca, https://github.com/DCC-Lab

import time
import struct
import re
import numpy as np
from typing import NamedTuple
import os

import usb.core
import usb.util

from hardwarelibrary.spectrometers.base import *
from hardwarelibrary.spectrometers.intelhexreader import *
import hardwarelibrary.utils as utils

class UnableToFindConfiguredSpectrometers(Exception):
    pass

class UnableToReadGainTable(Exception):
    pass

class DeviceIdentification(NamedTuple):
    model: str = None
    fifoSize: int = None
    gainIndex: int = None
    serialNumber: str = None

class DetectorType(enum.Enum):
    CCD2048 = "1"
    CCD1024 = "2"
    PDA2048 = "3"
    PDA1024 = "4"
    InGaAs512 = "5"
    InGaAs1024 = "6"
    Unknown = "X"

class InternalBufferSize(enum.IntEnum):
    unknown1 = 1
    large    = 2
    unknown3 = 3
    unknown4 = 4
    unknown5 = 5

"""
USB information available at https://www.beyondlogic.org/usbnutshell/usb6.shtml
"""
class RequestType(enum.IntEnum):
    outVendorDevice = usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE
    inVendorDevice = usb.util.CTRL_IN | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE

"""
Vendor-specific request for StellarNet and EZUSB, as accepted by the USB
standard and defined in the firmware for EZUSB. 
"""
class Request(enum.IntEnum):
    startAcquiringSpectrum      =   0xB2
    isSpectrumDataReady         =   0xB3
    setDigitalSamplingFrequency =   0xB4
    readDataFromAddress         =   0xB5
    writeAddressForRead         =   0xB6
    setFIFOFlags                =   0xB7

    EZUSBAnchorCommand          =   0xA0 #to reset ON/OFF device and load firmware

"""
Memory address for Reset on EZUSB chip
"""
class Value(enum.IntEnum):
    reset    = 0xE600

"""
Reset ON/OFF values
"""
class Data(enum.IntEnum):
    resetON  = 1
    resetOFF = 0

"""
Addresses where the firmware will look for information on the EZUSB chip.

TODO: Understand if they are limited to 8-bit only. For instance, the gain table is at 0x0100
but we must read from 0xff and ignore the first byte.
"""
class Address(enum.IntEnum):
    """ String containing device identification (model, serial number and features)"""
    deviceId = 0x20
    
    """ Strings for the wavelength calibration coefficients """
    c1 = 0x80
    c2 = 0xA0
    c3 = 0xC0
    c4 = 0xE0

    gainTable = 0xFF # Real table at 0x0100, ignore first byte.

class StellarNet(Spectrometer):
    classIdVendor = 0x0BD7
    classIdProduct = 0xA012

    classIdVendorRaw = 0x04b4
    classIdProductRaw = 0x8613

    detectorPixels = {
        DetectorType.CCD2048:2048,    # CCD - 2048
        DetectorType.CCD1024:1024,    # CCD - 1024
        DetectorType.PDA2048:2048,    # PDA - 2048
        DetectorType.PDA1024:1024,    # PDA - 1024
        DetectorType.InGaAs512:512,   # InGaAs - 512
        DetectorType.InGaAs1024:1024, # InGaAs - 1024
        DetectorType.Unknown:0        # PDA - 3600 (don't know the detector type for this one)
    }

    def __init__(self, serialNumber:str = None, idProduct:int = None, idVendor:int = None):
        """ 
        StellarNet spectrometer Black Comet spectrometer.
        """

        super().__init__(serialNumber=serialNumber, idProduct=idProduct, idVendor=idVendor)
        self.model = "StellarNet Black Comet"
        self.integrationTime = 10
        self.wavelength = None

        # USB-related variables
        self.usbDevice = None
        self.configuration = None
        self.interface = None
        self.inputEndpoints = []
        self.outputEndpoints = []
        self.epSpectrumData = []
        
        # Will raise exception if it cannot find a unique Spectrometer
        self.usbDevice = None
        usbDevices = utils.connectedUSBDevices(vidpids=StellarNet.vidpids())
        if len(usbDevices) == 1:
            self.usbDevice = usbDevices[0]

        # self.usbDevice = StellarNet.matchUniqueUSBDevice(idProduct=self.idProduct, serialNumber=self.serialNumber)

        """ Below are all the USB protocol details.  This requires reading
        the USB documentation, the Spectrometer documentation and many other 
        details. What follows may sound like gibberish.

        There is a single USB Configuration (default) with a single USB Interface 
        without alternate settings, so we can use (0,0).
        """
        self.usbDevice.set_configuration()
        self.configuration = self.usbDevice.get_active_configuration()
        self.interface = self.configuration[(0,0)]

        for endpoint in self.interface:
            """
            The endpoint address has the 8th bit set to 1 when it is an
            input. We can check with the bitwise operator & (and) 0x80
            (or usb.util.ENDPOINT_IN). It will be zero if an output and
            non-zero if an input. 
            """
            if endpoint.bEndpointAddress & usb.util.ENDPOINT_IN != 0:
                self.inputEndpoints.append(endpoint)
            else:
                self.outputEndpoints.append(endpoint)

            if endpoint.bEndpointAddress == usb.util.ENDPOINT_IN | 8:
                self.epSpectrumData = endpoint

        self.initializeDevice()

    def __del__(self):
        """
        When done, we must dispose of the usbDevice handle from PyUSB. If not, we will get 
        "permission denied" when attempting to access it with another object.
        """
        if self.usbDevice is not None:
            usb.util.dispose_resources(self.usbDevice)
            self.usbDevice = None

    @classmethod
    def vidpids(cls):
        return [(cls.classIdVendor, cls.classIdProduct), (cls.classIdVendorRaw, cls.classIdProductRaw)]


    def initializeDevice(self):
        """
        Perform necessary initialization before using the device.

        This will be integrated better with another framework (PyHardwareLibrary)
        and initialization will be better managed.  Right now, we assume that if
        the calibration was not set yet, the device is not initialized.
        """
        if self.wavelength is None:
            #self.flushEndpoints()
            self.doProgramInternalFIFO()
            self.setIntegrationTime(self.integrationTime)
            self.getCalibration()

    def flushEndpoints(self):
        """
        Flush the unused data in the input endpoints.
        """
        for endpoint in self.inputEndpoints:
            try:
                while True:
                    buffer = array.array('B',[0]*endpoint.wMaxPacketSize)
                    endpoint.read(size_or_buffer=buffer, timeout=100)
            except usb.core.USBTimeoutError as err:
                # This is expected and is not an error if the buffers
                # are empty.
                pass
            except Exception as err:
                print("Unable to flush buffers: {0}".format(err))

    def requestSpectrum(self):
        """
        Following a requestSpectrum call, the acquisition starts.  After "integrationTime" ms,
        we expect the data to be ready.
        """

        self.doWriteControlRequest(Request.startAcquiringSpectrum, data=[])

    def getSpectrumData(self) -> np.array:
        """ 
        Retrieve the spectral data as 16-bit integers, then convert to float.  You must call
        requestSpectrum first. If the spectrum is not ready yet, it will
        simply wait. The timeout is set short so it may timeout.  You would
        normally check with isSpectrumReady before calling this function.

        Returns
        -------
        spectrum : np.array(float) 

        The intensity spectrum, in 16-bit integers converted to float
        corresponding to each wavelength available in self.wavelength.
        """

        detectorType = self.doGetDetectorType()
        pixels = self.detectorPixels[detectorType]
        spectrumData = self.epSpectrumData.read(pixels*2)
        
        return np.array(struct.unpack_from('<{}H'.format(pixels), spectrumData),dtype=float)

    def getSpectrum(self, integrationTime=None) -> np.array:
        """ 
        This is the entry point to obtain a spectrum from the spectrometer. This will:
        1. change the integration time if needed.
        2. request a spectrum,
        3. wait until ready, then 
        4. actually retrieve and return the data.
        
        The timeout is set to the integration time plus 1 second.

        Parameters
        ----------
        integrationTime: int, default None 
            integration time in milliseconds, if None, will use the currently configured
            time.

        Returns
        -------

        spectrum : np.array(float)
            The spectrum, in 16-bit integers corresponding to each wavelength
            available in self.wavelength.
        """
        if integrationTime is not None:
            self.setIntegrationTime(integrationTime)

        self.requestSpectrum()
        timeOut = time.time() + float(self.integrationTime)/1000 + 1
        while not self.isSpectrumReady():
            time.sleep(0.001)
            if time.time() > timeOut:
                self.requestSpectrum() # makes no sense, let's request another one
                timeOut = time.time() + 1

        return self.getSpectrumData()
          
    def isSpectrumReady(self) -> bool:
        """ 
        If device is busy wait for next check else if device is ready wait
        before reading data. Note: reading data on StellarNet Black Comet
        without waiting  (time.sleep) occasionally results in a right-shifted spectrum
        which becomes more frequent with shorter integration times.
        """

        reponse = self.doReadControlRequest(Request.isSpectrumDataReady, wLength=2)
        
        time.sleep(.003)
        
        if reponse[1] == 0:
            return False

        return True

    def setIntegrationTime(self, value):
        """
        Set the integration time of the spectrum in millisecond.  The minimum value is 2 ms.
        It is stored for quick reference, and sent to the spectrometer.
        """
        self.integrationTime = value
        self.doSetIntegrationTime(value)

    def doSetIntegrationTime(self, timeInMs):
        """
        Send device timing information to the device.
    
        The base spectrometer class wants an integrtion time in (float) ms. However,
        we set the value on StellarNet in int16, se wo need to convert it.
        """
        time = int(timeInMs)

        x_timing = 1 # Seems to be the default in Stellarnet_Driver
        xt = 1<<(x_timing + 1)
        if time > 1:
            data = struct.pack(">HBB",time, xt, 0x1F)
        else:
            data = struct.pack(">HBB",2, xt, 0x0F)

        self.doWriteControlRequest(Request.setDigitalSamplingFrequency, data=data)

    def getSerialNumber(self):
        """
        Get the device serial number from the device identification string
        """
        deviceIdentification = self.doGetDeviceIdentification()
        return deviceIdentification.serialNumber

    def getCalibration(self):
        """
        Calibration coefficients for calibration of pixels. Yes they do look funny like that
        (c3 is the constant term and c4 is the cubic term). The equation is rewritten with 
        a0, a1, a2, a3 for readability.

        Important note: Some information is present at the end of the c1 and
        c4 strings, separated by spaces. The actual calibration coefficient
        is the first number: we therefore split on spaces and keep the first
        number as the coefficient and discard the other.
        """
        c1,_ = self.doReadString(Address.c1).split()
        c2 = float(self.doReadString(Address.c2))
        c3 = float(self.doReadString(Address.c3))
        c4,_ = self.doReadString(Address.c4).split()

        # wav[:,0] = ((wav[:,0]**3)*coeffs[3]/8.0 + (wav[:,0]**2)*coeffs[1]/4.0 + wav[:,0]*coeffs[0]/2.0 + coeffs[2])
        # wav[:,0] = ((wav[:,0]**3)*c4/8.0 + (wav[:,0]**2)*c2/4.0 + wav[:,0]*c1/2.0 + c3)

        a1 = float(c1)/2.0
        a2 = float(c2)/4.0
        a0 = float(c3)
        a3 = float(c4)/8.0


        detectorType = self.doGetDetectorType()
        pixels = self.detectorPixels[detectorType]

        self.wavelength = [ a0 + a1*x + a2*x*x + a3*x*x*x for x in range(pixels) ]

    def doGetDetectorType(self) -> DetectorType:
        """
        The detector type is stored in the 31st byte of the C1 coefficient as
        an ASCII number ("1","2", etc...). BEcause the readString command always reads 32 bytes,
        we read the whole thing, then split on spaces to extract the detector type.
        """
        try:
            c1, detectorString = self.doReadString(Address.c1).split()
            detectorType = DetectorType(detectorString)
        except:
            detectorType = DetectorType.Unknown

        return detectorType

    def doRead32Bytes(self, address) -> bytearray:
        """
        Read 32 bytes from 'address' in memory.  

        FIXME: Address appears to be a single byte and it does not appear to be possible to 
        read from 0x0100 for instance. In the returned data, the first byte is a repeat of the
        Request.readDataFromAddress value and is discarded.
        """
        addressPayload = [0, Address(address), 0]
        wLength =  0x01 + 0x20 # header byte + 32 bytes

        self.doWriteControlRequest(bRequest=Request.writeAddressForRead, data=addressPayload)
        data = self.doReadControlRequest(bRequest=Request.readDataFromAddress, wLength=wLength)
        return data[1:]

    def doReadString(self, address) -> str:
        """
        Read 32 bytes from memory then convert the bytearray into a strirng
        using standarda UTF-8 (ASCII) characters.
        """

        return self.doRead32Bytes(address).decode("utf-8")

    def doWriteControlRequest(self, bRequest:Request, data:bytearray):
        """
        Convenience function to send control request (i.e. commands to the
        CTL#0 endpoint) 1. to write from the host to the device, 2. to the
        actual Device (target) interpreted as a 3. vendor-specific command

        bRequest is the USB bRequest.  The specific request for the StellarNet spectrometer
        are defined as a 'Request' enum. data is specific to the request.
        """
        self.usbDevice.ctrl_transfer(RequestType.outVendorDevice, 
                                     bRequest=bRequest,
                                     wValue=0, 
                                     wIndex=0,
                                     data_or_wLength=data)

    def doReadControlRequest(self, bRequest:Request, wLength:int) -> bytearray:
        """
        Convenience function to send control request (i.e. commands to the
        CTL#0 endpoint) 1. to read from the usb device, 2. from the actual
        Device (target) interpreted as a 3. vendor-specific command.

        bRequest is the USB bRequest.  The specific request for the StellarNet spectrometer
        are defined as a 'Request' enum. data is specific to the request.
        """
        data = self.usbDevice.ctrl_transfer(RequestType.inVendorDevice,
                                     bRequest=bRequest,
                                     wValue=0,
                                     wIndex=0,
                                     data_or_wLength=wLength)
        return bytearray(data)

    def doGetDeviceIdentification(self) -> DeviceIdentification:
        """
        The device identification string looks like:
        "BLACK CXR-SR 50#21032432f2g1" 
        The alphabetical characters after # and the digits indicate features:
            f2: Large FIFO buffer
            g1: gain settings
        """

        deviceIdentification = self.doReadString(address=Address.deviceId)
        match = re.search(r"(.+)\s*#(\d+)f(\d)g(\d)", deviceIdentification, flags=re.IGNORECASE)
        if match:
            model = match.group(1)
            serialNumber = match.group(2)
            fifoSize = int(match.group(3))
            gainValue = int(match.group(4))
            return DeviceIdentification(model, fifoSize, gainValue, serialNumber)

        return None

    def saveGainToEEPROM(self, index=None):
        """
        The gain and base values for the amplification on the device.  The
        correct values are stored in the deviceIdentification string, and
        appear as "g1" "g2", etc... The gain index therefore goes from 1 to 5
        to avoid any confusion, but our table (in Python) is zero-based, that
        is why we use index-1 in the code. We use the same index for the base
        value.
        """

        if index is None:
            deviceIdentification = self.doGetDeviceIdentification()
            index = deviceIdentification.gainIndex

        if index not in [1,2,3,4,5]:
            raise Exception("Gain index must be 1,2,3,4 or 5")

        setGainCommand = 0
        setBaseCommand = 1

        gainTable = self.doGetGainTable()
        gain = gainTable[(index-1)] # 1 is the first entry in the table
        self.doWriteControlRequest(Request.setFIFOFlags, data= [setGainCommand, gain, 0, 0])

        base = gainTable[(index-1)+5]
        self.doWriteControlRequest(Request.setFIFOFlags, data= [setBaseCommand, base, 0, 0])

    def doGetGainTable(self):
        """
        5 gains followed by 5 bases are stored starting at 0x100, but we
        cannot read memory locations with 16-bit addresses, therefore we read
        from 0xFF and discard the first byte.  
        """
        table = self.doReadString(address=Address.gainTable)

        match = re.search(r".(.{3})(.{3})(.{3})(.{3})(.{3})(.{3})(.{3})(.{3})(.{3})(.{3})", table, flags=re.IGNORECASE)
        if match:
            return [ int(x) for x in match.groups()]
        else:
            raise UnableToReadGainTable()

    @property
    def hasLargeFIFO(self) -> bool:
        """
        In the device identification string, a "f1", "f2", etc... is an indicator of the buffer size.
        f2 means a large buffer, which we can the configure accordingly.
        """
        deviceIdentification = self.doGetDeviceIdentification()
        return deviceIdentification.fifoSize == 2
    
    def doProgramInternalFIFO(self):
        setFIFOSizeCommand = 3
        programFIFOCommand = 2
        frames = 128
        xtrate = 0xF8

        if self.hasLargeFIFO:
            self.doWriteControlRequest(bRequest=Request.setFIFOFlags, data=[setFIFOSizeCommand, frames, 0, 0])
            self.doWriteControlRequest(bRequest=Request.setFIFOFlags, data=[programFIFOCommand, xtrate, 0, 0])

    @classmethod
    def loadFirmwareOnConnectedDevices(cls):
        rawUSBDevices = cls.findRawDevices()
        if len(rawUSBDevices) != 0:
            cls.loadFirmwareOntoRawDevices(rawUSBDevices)
            cls.disposeRawDevices(rawUSBDevices)


    @classmethod
    def connectedUSBDevices(cls, idProduct=None, serialNumber=None) -> list:
        """ 
        Return a list of supported USB devices that are currently connected.
        If idProduct is provided, match only these products. If a serial
        number is provided, return the matching device otherwise return an
        empty list. If no serial number is provided, return all devices.

        StellarNet devices appear as "raw" Cypress EZ-USB devices when first
        connected and will need to have a firmware loaded to be functional.
        We start by locating all these raw devices with their idVendor and
        idProduct, load the StellarNet firmware, and then and only then, will
        we get access to devices with the StellarNet idVendor and idProduct
        for the BlackComet.  At that point, we use the function from the base
        class.

        Parameters
        ----------
        idProduct: int Default: None
            The USB idProduct to match
        serialNumber: str Default: None
            The serial number to match, when there are still more than one device after
            filtering out the idProduct.  If there is a single match, the serial number
            is disregarded.

        Returns
        -------

        devices: list of Device
            A list of connected devices matching the criteria provided
        """
        rawUSBDevices = cls.findRawDevices()
        if len(rawUSBDevices) != 0:
            cls.loadFirmwareOntoRawDevices(rawUSBDevices)
            cls.disposeRawDevices(rawUSBDevices)

        return super().connectedUSBDevices(idProduct, serialNumber)

    @classmethod
    def readFirmwareDefinition(cls, firmwareFilePath=None) -> IntelHexReader:
        try:
            if firmwareFilePath is None:
                firmwareFilePath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "stellarnet.hex")

            return IntelHexReader(filepath=firmwareFilePath)
        except Exception as err:
            raise RuntimeError("Unable to read firmware file for StellarNet spectrometer {0}. Please contact StellarNet.".format(err))

    @classmethod
    def findRawDevices(cls) -> list:
        idVendorRaw = 0x04b4
        idProductRaw = 0x8613
        return list(usb.core.find(find_all=True, 
                                  idVendor=idVendorRaw, 
                                  idProduct=idProductRaw))

    @classmethod
    def disposeRawDevices(cls, rawUSBDevices):
        for device in rawUSBDevices:
            usb.util.dispose_resources(device)

    @classmethod
    def loadFirmwareOntoRawDevices(cls, usbDevices):
        firmwareReader = cls.readFirmwareDefinition()

        for usbDevice in usbDevices:
            cls.beginFirmwareLoading(usbDevice)        
            cls.loadFirmware(usbDevice, firmwareReader.records)        
            cls.endFirmwareLoading(usbDevice)

        timeout = time.time() + 5 # It takes approximately 1.7 seconds
        updatedDevices = []
        while len(updatedDevices) == 0:
            time.sleep(0.5)
            updatedDevices = list(usb.core.find(find_all=True, 
                                       idVendor=cls.idVendor,
                                       idProduct=cls.idProduct))
            if time.time() > timeout:
                raise UnableToFindConfiguredSpectrometers()

    @classmethod
    def beginFirmwareLoading(cls, usbDevice):
        """
        This puts the EZ-USB CPU on usbDevice in reset mode to allow loading a firmware.
        Must be matched with a endFirmwareLoading() call.

        All information regarding this EZ-USB specific command is found here:
        https://community.cypress.com/t5/Knowledge-Base-Articles/Examples-showing-how-to-download-firmware-to-a-EZ-USB-AN21xx-FX/ta-p/253105
        """

        usbDevice.ctrl_transfer(RequestType.outVendorDevice, 
                                Request.EZUSBAnchorCommand,
                                wValue=Value.reset,
                                wIndex=0,
                                data_or_wLength=[1])

    @classmethod
    def loadFirmware(cls, usbDevice, records):
        """
        Load the complete firmware records obtained from IntelHexReader file
        """

        for record in records:
            if record.type == RecordType.data:
                usbDevice.ctrl_transfer(RequestType.outVendorDevice, 
                                        Request.EZUSBAnchorCommand,
                                        wValue=record.address,
                                        wIndex=0,
                                        data_or_wLength=record.data)

    @classmethod
    def endFirmwareLoading(cls, usbDevice):
        """
        This stops the EZ-USB CPU reset mode to indicate firmware was loaded.
        """

        usbDevice.ctrl_transfer(RequestType.outVendorDevice, 
                                Request.EZUSBAnchorCommand,
                                wValue=Value.reset,
                                wIndex=0,
                                data_or_wLength=[0])
