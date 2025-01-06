# Errors
class NvnaDeviceNotFound(Exception):
    """Nano VNA exception for device not found. 
    Means that by inspecting the serial port, no device is found
    for the default or specified VID and PID.

    Args:
        message (str): message passed when raised
    """
    def __init__(self, message="No NanoVNA found, if specific VID/PID, specify at instanciation"):
        self.message = message
        super().__init__(self.message)


class NvnaDeviceNotReachable(Exception):
    """Nano VNA exception for device not reachable.
    Means that something when wrong when trying to initialise
    the serial connection with the specified VID and PID.

    Args:
        message (_type_): _description_
    """
    def __init__(self, vid, pid, message="Something went wrong when connecting to VID/PID: "):
        self.vid = vid
        self.pid = pid
        self.message = message
        super().__init__(self.message + str(self.vid) + '/' + str(self.pid))


class NvnaDeviceNotConnected(Exception):
    """Nano VNA exception for device not connected.
    Means that there is a request to send a command to the device 
    without a device beeing actually connected.

    Args:
        message (str): message passed when raised
    """
    def __init__(self, message="No NanoVNA device connected"):
        self.message = message
        super().__init__(self.message)


# Warnings
class NvnaIDNotAvailable(Warning):
    """_summary_

    Args:
        Warning (_type_): _description_
    """
    def __init__(self, ID_already_attributed, ID_decided, message="Requested ID already attributed, automatic ID attribution"):
        self.ID_1 = ID_already_attributed
        self.ID_2 = ID_decided
        self.message = message
        super().__init__(self.message+' '+str(self.ID_1)+' '+str(self.ID_2))