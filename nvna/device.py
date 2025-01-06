import serial
from serial.tools import list_ports
import weakref

from .exceptions import NvnaDeviceNotFound, NvnaIDNotAvailable

nvna_vid = 0x0483   # 1155
nvna_pid = 0x5740   # 22336


def get_device(vid=nvna_vid, pid=nvna_pid):
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


class NVNA:
    """
    A class to handle NanoVNA devices.
    """
    nvna_instances = weakref.WeakSet()
    nvna_IDs = []

    def __init__(self, ID = None, connect=True, vid=None, pid=None) -> None:
        if vid is not None:
            self.vid = vid
        else:
            self.vid = nvna_vid
        if pid is not None:
            self.pid = pid
        else:
            self.pid = nvna_pid
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

    def __del__(self):
        # unconect if needed
        if self.connected:
            self._disconnect()
        # remove from instance list
        NVNA.nvna_IDs.remove(self.ID)
        NVNA.nvna_instances.remove(self)

    def _connect(self):
        self.device_info = get_device(vid=self.vid, pid=self.pid)
        if self.device_info is not None:
            try:
                self.serial = serial.Serial(self.device_info['device'])
            except:
                raise # to be completed
        else:
            raise NvnaDeviceNotFound

    def _disconnect(self):
        self.serial.close()

    def get_ID(self):
        return self.ID
    
    def send_command(self, command):
        if self.connected:
            self.serial.self.serial.write(cmd.encode())
            self.serial.readline() # discard empty line
    
    def set_sweep(self, start, stop):
        if start is not None:
            self.send_command("sweep start %d\r" % start)
        if stop is not None:
            self.send_command("sweep stop %d\r" % stop)

    def set_frequency(self, freq):
        if freq is not None:
            self.send_command("freq %d\r" % freq)

    def set_port(self, port):
        if port is not None:
            self.send_command("port %d\r" % port)

    def set_gain(self, gain):
        if gain is not None:
            self.send_command("gain %d %d\r" % (gain, gain))

    def set_offset(self, offset):
        if offset is not None:
            self.send_command("offset %d\r" % offset)