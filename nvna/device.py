import serial
from serial.tools import list_ports
import weakref
import numpy as np

from .exceptions import NvnaDeviceNotFound, NvnaIDNotAvailable

###############
## Constants ##
###############
nvna_constants = {
    'nvna_vid': 0x0483,   # 1155
    'nvna_pid': 0x5740,   # 22336
    'nvna_FMIN': 5e4,
    'nvna_FMAX': 3e9,
    'nvna_NptsMIN': 11,
    'nvna_NptsMAX': 201,
}

###############
## Functions ##
###############
def get_device(vid=nvna_constants['nvna_vid'], pid=nvna_constants['nvna_pid']):
    device_info = None
    device_list = list_ports.comports()
    for device in device_list:
        if device.vid == vid and device.pid == pid:
            device_info = {
                'vid': vid,
                'pid': pid,
                'device': device.device,
                'serial_number': device.serial_number,
                'manufacturer': device.manufacturer,
                'description': device.description,
                'name': device.name,
            }
    return device_info

#############
## Classes ##
#############
class NVNA:
    """
    A class to handle NanoVNA devices.
    """
    nvna_instances = weakref.WeakSet()
    nvna_IDs = []

    def __init__(self, ID = None, connect=True, vid=None, pid=None) -> None:
        """Initialize a NanoVNA device as an instant of an object

        Args:
            ID (int, optional): 
                identifier for the device. 
                If not specified, the first device found is set to 0, then a new device as the incremented ID from the last detected.
            connect (bool, optional): _
                Actually Connect to the device, can be False for debug. 
                Defaults to True.
            vid (int, optional): 
                Vendor ID, if not specified, set to the default NanoVNA Vendor ID (1155). 
                Defaults to None.
            pid (int, optional): 
                Product ID, if not specified, set to the default NanoVNA Product ID (22336). 
                Defaults to None.

        Raises:
            NvnaIDNotAvailable: _description_
        """
        if vid is not None:
            self.vid = vid
        else:
            self.vid = nvna_constants['nvna_vid']
        if pid is not None:
            self.pid = pid
        else:
            self.pid = nvna_constants['nvna_pid']
        self.connected = False
        # check ID availability, attribute different if not available
        # and add to the instances list
        if ID not in NVNA.nvna_IDs:
            NVNA.nvna_instances.add(self)
            NVNA.nvna_IDs.append(ID)
            self.ID = ID
        else:
            new_ID = 0
            while new_ID in NVNA.nvna_IDs:
                new_ID += 1
            NVNA.nvna_instances.add(self)
            NVNA.nvna_IDs.append(new_ID)
            self.ID = new_ID
            raise NvnaIDNotAvailable(ID, new_ID)
        # if requested, connect the device
        self.serial = None
        if connect:
            self._connect()
            self.connected = True
        # last measurement and calibration
        self._frequencies = None
        self._S11 = None
        self._S11_OPEN = None
        self._S11_SHORT = None
        self._S11_LOAD = None
        self._S11_THROUGH = None
        self._S21 = None
        self._S21_OPEN = None
        self._S21_SHORT = None
        self._S21_LOAD = None
        self._S11_THROUGH = None

    def __del__(self):
        """Class destructor
        """
        # unconect if needed
        if self.connected:
            self._disconnect()
        # remove from instance list
        NVNA.nvna_IDs.remove(self.ID)
        print(len(NVNA.nvna_instances))
        NVNA.nvna_instances.remove(self)

    def _connect(self):
        """_summary_

        Raises:
            NvnaDeviceNotFound: _description_
        """
        self.device_info = get_device(vid=self.vid, pid=self.pid)
        if self.device_info is not None:
            try:
                self.serial = serial.Serial(self.device_info['device'], baudrate=115200)
            except:
                raise # to be completed
        else:
            raise NvnaDeviceNotFound

    def _disconnect(self):
        self.serial.close()

    def get_ID(self):
        """Get the user ID (not equal to VID nor VID) of the device associated with the current instace

        Returns:
            int: user ID of the device
        """
        return self.ID

    def send_command(self, command):
        """Send a command to the device.
        Basically sends an encoded string  by serial interface. 
        Not a user friendly command, should not be used by the end-user, prefer dedicated methods.

        Args:
            command (str): 
                command to send to the NanoVNA
        """
        if self.connected:
            self.serial.write(command.encode())
            self.serial.readline() # discard empty line

    def get_data(self):
        """Get data from the device.
        Basiccally recieve an encoded string  by serial interface.
        Not user friendly, should not be used by the end-user, prefer measurement methods.

        Returns:
            _type_: _description_
        """
        result = ''
        line = ''
        while True:
            c = self.serial.read().decode('utf-8')
            if c == chr(13):
                next # ignore CR
            line += c
            if c == chr(10):
                result += line
                line = ''
                next
            if line.endswith('ch>'):
                # stop on prompt
                break
        return result

    def set_sweep(self, start=None, stop=None, n_points=None):
        """Set the frequencial sweep of the NanoVNA.
        This methods sets the minimum and maximum frequncies of the sweep.

        Args:
            start (int):
                start frequency of the sweep, in Hz
            stop (int):
                stop frequency of the sweep, in Hz
            n_points (int, optional):
                number of points in the sweep
        """
        # bounds
        if start is not None:
            if start < nvna_constants['nvna_FMIN']:
                actual_start = nvna_constants['nvna_FMIN']
            else:
                actual_start = int(start)
        if stop is not None:
            if stop > nvna_constants['nvna_FMAX']:
                actual_stop = nvna_constants['nvna_FMAX']
            else:
                actual_stop = int(stop)
        # to prevent dimmy students issues
        if start is not None and stop is not None:
            if stop < start:
                actual_start = int(stop)
                actual_stop = int(start)
        if start is not None:
            self.send_command("sweep start %d\r" % actual_start)
        if stop is not None:
            self.send_command("sweep stop %d\r" % actual_stop)
        if n_points is not None:
            actual_npoints = int(n_points)
            # bounding
            if actual_npoints < nvna_constants['nvna_NptsMIN']:
                actual_npoints = nvna_constants['nvna_NptsMIN']
            elif actual_npoints > nvna_constants['nvna_NptsMAX']:
                actual_npoints = nvna_constants['nvna_NptsMAX']
            # sending
            self.send_command("sweep points %d\r" % actual_npoints)

    def get_frequencies(self):
        self.send_command("frequencies\r")
        data = self.get_data()
        freqs = []
        for line in data.split('\n'):
            if line:
                freqs.append(float(line))
        self._frequencies = np.array(freqs, dtype=np.float64)
        return self._frequencies

    def get_S_parameters(self, start, stop, Npoints):
        actual_start = int(start)
        actual_stop = int(stop)
        actual_Npoints = int(Npoints)

        self.send_command("scan %d %d %d 7\r"%(actual_start, actual_stop, actual_Npoints))
        data = self.get_data()
        freqs = []
        S11 = []
        S21 = []
        for line in data.split('\n'):
            if line:
                sline = line.split()
                freqs.append(float(sline[0]))
                S11.append(float(sline[1])+1j*float(sline[2]))
                S21.append(float(sline[3])+1j*float(sline[4]))
        self._frequencies = np.array(freqs, dtype=np.float64)
        self._S11 = np.array(S11, dtype=np.complex128)
        self._S21 = np.array(S21, dtype=np.complex128)
        return self._frequencies, self._S11, self._S21

    def get_S11(self, start, stop, Npoints):
        actual_start = int(start)
        actual_stop = int(stop)
        actual_Npoints = int(Npoints)

        self.send_command("scan %d %d %d 3\r"%(actual_start, actual_stop, actual_Npoints))
        data = self.get_data()
        freqs = []
        S11 = []
        for line in data.split('\n'):
            if line:
                sline = line.split()
                freqs.append(float(sline[0]))
                S11.append(float(sline[1])+1j*float(sline[2]))
        self._frequencies = np.array(freqs, dtype=np.float64)
        self._S11 = np.array(S11, dtype=np.complex128)
        return self._frequencies, self._S11


    def get_S21(self, start, stop, Npoints):
        actual_start = int(start)
        actual_stop = int(stop)
        actual_Npoints = int(Npoints)

        self.send_command("scan %d %d %d 6\r"%(actual_start, actual_stop, actual_Npoints))
        data = self.get_data()
        freqs = []
        S21 = []
        for line in data.split('\n'):
            if line:
                sline = line.split()
                freqs.append(float(sline[0]))
                S21.append(float(sline[1])+1j*float(sline[2]))
        self._frequencies = np.array(freqs, dtype=np.float64)
        self._S21 = np.array(S21, dtype=np.complex128)
        return self._frequencies, self._S21
    
    def SOL_S11_calibration(self):
        pass
