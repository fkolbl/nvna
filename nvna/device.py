import serial
from serial.tools import list_ports
import weakref
import numpy as np

from .exceptions import NvnaDeviceNotFound, NvnaIDNotAvailable, NvnaDeviceNotConnected


###############
## Constants ##
###############
nvna_constants = {
    "nvna_vid": 0x0483,  # 1155
    "nvna_pid": 0x5740,  # 22336
    "nvna_FMIN": 5e5,
    "nvna_FMAX": 3e9,
    "nvna_NptsMIN": 11,
    "nvna_NptsMAX": 201,
}

nvna_defaults = {
    "nvna_FSTART": 5e5,
    "nvna_FSTOP": 2.5e9,
    "nvna_Npts": 201,
}


###############
## Functions ##
###############
def get_device(vid=nvna_constants["nvna_vid"], pid=nvna_constants["nvna_pid"]):
    device_info = None
    device_list = list_ports.comports()
    for device in device_list:
        if device.vid == vid and device.pid == pid:
            device_info = {
                "vid": vid,
                "pid": pid,
                "device": device.device,
                "serial_number": device.serial_number,
                "manufacturer": device.manufacturer,
                "description": device.description,
                "name": device.name,
            }
    return device_info


def S2Z(S, z0=50.0):
    """_summary_

    Args:
        S (float or numpy array): Scattering parameter
        z0 (float, optional): caracteristic impedance. Defaults to 50.0.

    Returns:
        Z: Impedance converted from the scattering parameter for the caracteristic impedance
    """

    return z0 * ((1 + S) / (1 - S))


def Z2S(Z, z0=50.0):
    """_summary_

    Args:
        Z (float or numpy array): Impedance
        z0 (float, optional): caracteristic impedance. Defaults to 50.0.

    Returns:
        S: Scattering parameter computed from the impedance and the caracteristic impedance
    """
    z = Z / z0
    return (z - 1) / (z + 1)


def S2Z_void(S):
    """
    Warning: used for teaching only, prevent any automated solution to force student to code,
    """
    print("Warning: you should specify the Scattering to Impedance convertion")
    return np.zeros(np.shape(S), dtype=np.complex128)


def Z_de_embed(S, Z_short, Z_open, Z_load, z0=50):
    """_summary_

    Args:
        S (numpy array): scattering parameter
        Z_short (numpy array): calibration short measurement
        Z_open (numpy array):  calibration open measurement
        Z_load (numpy array):  calibration load measurement
        z0 (int, optional): caracteristic impedance. Defaults to 50.

    Returns:
        Z: de-embedded impedance calculated from the scattering parameter for a calibration
    """
    Z_m = S2Z(S)
    num = z0 * (Z_m - Z_short) * (Z_open - Z_load)
    denom = (Z_open - Z_m) * (Z_load - Z_short)
    return num / denom


def Z_de_embed_void(S, Z_short, Z_open, Z_load):
    """
    Warning: used for teaching only, prevent any automated solution to force student to code,
    """
    print("Warning: you should specify the Scattering to Impedance convertion")
    return np.zeros(np.shape(S), dtype=np.complex128)


def save_1PCal_to_file(fname, f, SCal_S, SCal_O, SCal_L):
    """Saves the calibration to a csv file

    Args:
        fname (stre): _description_
        f (numpy array): frequency vector of the calibration
        SCal_S (numpy array): Scattering vector of the calibration with short termination
        SCal_O (numpy array): Scattering vector of the calibration with open termination
        SCal_L (numpy array): Scattering vector of the calibration with load termination
    """
    ZCal_S = S2Z(SCal_S)
    ZCal_O = S2Z(SCal_O)
    ZCal_L = S2Z(SCal_L)
    with open(fname, "w") as file:
        file.write("#f, S11_short, S11_open, S11_load, Zin_short, Zin_open, Zin_load\n")
        for i in range(len(f)):
            file.write(
                "{}, {}, {}, {}, {}, {}, {}\n".format(
                    f[i],
                    SCal_S[i],
                    SCal_O[i],
                    SCal_L[i],
                    ZCal_S[i],
                    ZCal_O[i],
                    ZCal_L[i],
                )
            )


def load_1PCal_from_file(fname):
    """load a calibration from a file

    Args:
        fname (str): filename or path

    Returns:
        f (numpy array): _description_
        SCal_S (numpy array): scattering parameter for the short calibration
        SCal_0 (numpy array): scattering parameter for the open calibration
        SCal_L (numpy array): scattering parameter for the load calibration
        ZCal_S (numpy array): impedance for the short calibration
        ZCal_O (numpy array): impedance for the open calibration
        ZCal_L (numpy array): impedance for the load calibration
    """
    data = np.loadtxt(fname, skiprows=1, delimiter=",", dtype=np.complex128)
    f = np.real(data[:, 0])
    SCal_S = data[:, 1]
    SCal_O = data[:, 2]
    SCal_L = data[:, 3]
    ZCal_S = data[:, 4]
    ZCal_O = data[:, 5]
    ZCal_L = data[:, 6]
    return f, SCal_S, SCal_O, SCal_L, ZCal_S, ZCal_O, ZCal_L


def save_1Pmeasurement_to_file(fname, freq, S11, Z):
    """Save one port measurement to a file

    Args:
        fname (str): filename
        freq (numpy array): frequency of measurement
        S11 (numpy array): scattering parameter
        Z (numpy array): impedance
    """
    with open(fname, "w") as file:
        file.write("#f, S11, Z\n")
        for i in range(len(freq)):
            file.write("{}, {}, {}\n".format(freq[i], S11[i], Z[i]))


#############
## Classes ##
#############
class NVNA:
    """
    A class to handle NanoVNA devices.
    """

    nvna_instances = weakref.WeakSet()
    nvna_IDs = []

    def __init__(
        self, ID=None, connect=True, vid=None, pid=None, fcal=None, Tmode=False
    ) -> None:
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
            fcal (str, optional):
                calibration file path, if not specified, no calibration is used.
            Tmode (bool, optional):
                Teacher mode (the scattering parameter convertion and the de-embedding are performed automatically)

        Raises:
            NvnaIDNotAvailable: _description_
        """
        if vid is not None:
            self.vid = vid
        else:
            self.vid = nvna_constants["nvna_vid"]
        if pid is not None:
            self.pid = pid
        else:
            self.pid = nvna_constants["nvna_pid"]
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
        # config
        self._fmin = None
        self._fmax = None
        self._npts = None
        # last measurement and calibration
        self._EMPTY = True
        self._1PCAl = False
        self._FULLCAL = False
        self._frequencies = None
        self._S11 = None
        self._S11_OPEN = None
        self._S11_SHORT = None
        self._S11_LOAD = None
        self._Z_OPEN = None
        self._Z_SHORT = None
        self._Z_LOAD = None
        self._S11_THROUGH = None
        self._S21 = None
        self._S21_OPEN = None
        self._S21_SHORT = None
        self._S21_LOAD = None
        self._S11_THROUGH = None
        # load cal if specified
        if fcal is not None:
            print("\t... loading specified calibration")
            self.load_1PCal(fcal)
        # functions for S2Z and deembeding
        self._Tmode = Tmode
        self.scattering2impedance = S2Z_void
        self.Z_de_embedd = Z_de_embed_void
        if self._Tmode:
            self.scattering2impedance = S2Z
            self.Z_de_embedd = Z_de_embed

    def __del__(self):
        """Class destructor"""
        # unconect if needed
        if self.connected:
            self._disconnect()
        # remove from instance list
        NVNA.nvna_IDs.remove(self.ID)
        print(len(NVNA.nvna_instances))
        NVNA.nvna_instances.remove(self)

    def _connect(self):
        """Connect to a physical device, internal use only

        Raises:
            NvnaDeviceNotFound: _description_
        """
        self.device_info = get_device(vid=self.vid, pid=self.pid)
        if self.device_info is not None:
            try:
                self.serial = serial.Serial(self.device_info["device"], baudrate=115200)
                self.set_sweep(
                    nvna_defaults["nvna_FSTART"],
                    nvna_defaults["nvna_FSTOP"],
                    nvna_defaults["nvna_Npts"],
                )
                self._fmin = nvna_defaults["nvna_FSTART"]
                self._fmax = nvna_defaults["nvna_FSTOP"]
                self._npts = nvna_defaults["nvna_Npts"]
            except:
                raise NvnaDeviceNotConnected
        else:
            raise NvnaDeviceNotFound

    def _disconnect(self):
        """Disconnect from the physical device, internal use only"""
        self.serial.close()

    def get_ID(self):
        """Get the user ID (not equal to VID nor VID) of the device associated with the current instace

        Returns:
            int: user ID of the device
        """
        return self.ID

    def load_1PCal(self, fname):
        """Load a full one port Short Open Load calibration from a file.

        Args:
            fname (str): filename
        """
        f, SCal_S, SCal_O, SCal_L, ZCal_S, ZCal_O, ZCal_L = load_1PCal_from_file(fname)
        # get cal in instance
        self._1PCAl = True
        self._frequencies = f
        self._S11_OPEN = SCal_O
        self._S11_SHORT = SCal_S
        self._S11_LOAD = SCal_L
        self._Z_OPEN = ZCal_O
        self._Z_SHORT = ZCal_S
        self._Z_LOAD = ZCal_L
        # retrieve config
        self._fmin = self._frequencies[0]
        self._fmax = self._frequencies[-1]
        self._npts = len(self._frequencies)

    def save_1PCal(self, fname="nvna_current_cal.csv"):
        """Save the current 1 full port calibration in a file

        Args:
            fname (str, optional): _description_. Defaults to "nvna_current_cal.csv".
        """
        if self._1PCAl or self._FULLCAL:
            save_1PCal_to_file(
                fname,
                self._frequencies,
                self._S11_SHORT,
                self._S11_OPEN,
                self._S11_LOAD,
            )
        else:
            print("Warning: NVNA is not calibrated yet")

    def attach_Scattering2Impedance_converter(self, userfunction):
        """Attach a custom function to the device for Sattering parameter to impedance convertion

        Args:
            userfunction (function):
                function to be called with S11 values and optional Z value as input and return Z values
        """
        self.scattering2impedance = userfunction

    def attach_Zdeembed_converter(self, userfunction):
        """Attach a custom function to the device for Sattering parameter and deembedding

        Args:
            userfunction (function): custom function to be called for deembedding
        """
        self.Z_de_embedd = userfunction

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
            self.serial.readline()  # discard empty line

    def get_data(self):
        """Get data from the device.
        Basiccally recieve an encoded string  by serial interface.
        Not user friendly, should not be used by the end-user, prefer measurement methods.

        Returns:
            _type_: _description_
        """
        result = ""
        line = ""
        while True:
            c = self.serial.read().decode("utf-8")
            if c == chr(13):
                next  # ignore CR
            line += c
            if c == chr(10):
                result += line
                line = ""
                next
            if line.endswith("ch>"):
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
            if start < nvna_constants["nvna_FMIN"]:
                actual_start = nvna_constants["nvna_FMIN"]
            else:
                actual_start = int(start)
        if stop is not None:
            if stop > nvna_constants["nvna_FMAX"]:
                actual_stop = nvna_constants["nvna_FMAX"]
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
            if actual_npoints < nvna_constants["nvna_NptsMIN"]:
                actual_npoints = nvna_constants["nvna_NptsMIN"]
            elif actual_npoints > nvna_constants["nvna_NptsMAX"]:
                actual_npoints = nvna_constants["nvna_NptsMAX"]
            # sending
            self.send_command("sweep points %d\r" % actual_npoints)

    def get_frequencies(self):
        """Get the frequency vector of the current sweep

        Returns:
            np.array: array of frequencies in Hz
        """
        self.send_command("frequencies\r")
        data = self.get_data()
        freqs = []
        for line in data.split("\n"):
            if line:
                freqs.append(float(line))
        self._frequencies = np.array(freqs, dtype=np.float64)
        return self._frequencies

    def get_S_parameters(self, start, stop, Npoints):
        """Get the S parameters from the device
        Note that last measurement is stored in the instance at _frequencies, _S11, _S21
        attributes

        Args:
            start (float): starting frequency of the measurement in Hz
            stop (float): stopping frequency of the measurement in Hz
            Npoints (int): number of points in the frequency sweep

        Returns:
            freqencies (np.array): array of frequencies in Hz
            S11 (np.array): reflection S parameter
            S21 (np.array): transmission S parameter
        """
        actual_start = int(start)
        actual_stop = int(stop)
        actual_Npoints = int(Npoints)

        self.send_command(
            "scan %d %d %d 7\r" % (actual_start, actual_stop, actual_Npoints)
        )
        data = self.get_data()
        freqs = []
        S11 = []
        S21 = []
        for line in data.split("\n"):
            if line:
                sline = line.split()
                freqs.append(float(sline[0]))
                S11.append(float(sline[1]) + 1j * float(sline[2]))
                S21.append(float(sline[3]) + 1j * float(sline[4]))
        self._frequencies = np.array(freqs, dtype=np.float64)
        self._S11 = np.array(S11, dtype=np.complex128)
        self._S21 = np.array(S21, dtype=np.complex128)
        return self._frequencies, self._S11, self._S21

    def get_S11(self, start, stop, Npoints):
        """Launch a S11 measurement and get results

        Args:
            start (float): starting frequency
            stop (float): stopping frequency
            Npoints (int): numpy of measurement frequencies

        Returns:
            freq (numpy array): frequencies of measurement
            S11 (numpy array): reflection S parameter
        """
        actual_start = int(start)
        actual_stop = int(stop)
        actual_Npoints = int(Npoints)

        self.send_command(
            "scan %d %d %d 3\r" % (actual_start, actual_stop, actual_Npoints)
        )
        data = self.get_data()
        freqs = []
        S11 = []
        for line in data.split("\n"):
            if line:
                sline = line.split()
                freqs.append(float(sline[0]))
                S11.append(float(sline[1]) + 1j * float(sline[2]))
        self._frequencies = np.array(freqs, dtype=np.float64)
        self._S11 = np.array(S11, dtype=np.complex128)
        return self._frequencies, self._S11

    def get_S21(self, start, stop, Npoints):
        """Launch a S21 measurement and get results

        Args:
            start (float): starting frequency
            stop (float): stopping frequency
            Npoints (int): numpy of measurement frequencies

        Returns:
            freq (numpy array): frequencies of measurement
            S21 (numpy array): reflection S parameter
        """
        actual_start = int(start)
        actual_stop = int(stop)
        actual_Npoints = int(Npoints)

        self.send_command(
            "scan %d %d %d 6\r" % (actual_start, actual_stop, actual_Npoints)
        )
        data = self.get_data()
        freqs = []
        S21 = []
        for line in data.split("\n"):
            if line:
                sline = line.split()
                freqs.append(float(sline[0]))
                S21.append(float(sline[1]) + 1j * float(sline[2]))
        self._frequencies = np.array(freqs, dtype=np.float64)
        self._S21 = np.array(S21, dtype=np.complex128)
        return self._frequencies, self._S21

    def PORT1_calibration(
        self, fmin=None, fmax=None, n_pts=None, n_average=6, savecal=True
    ):
        """
        Calibrate the S11 measurement using SOL technique.
        Does not deembed measurements, but stores the calibration vectors in
        _S11_OPEN, _S11_SHORT, _S11_LOAD attributes

        Returns:
            None
        """
        print(
            """-----------------------------------------------------\n
-- Short Open Load calibration for S11 one port use --\n
-----------------------------------------------------\n"""
        )
        # update device config if necessary
        if fmin is not None:
            self._fmin = fmin
        else:
            self._fmin = nvna_constants["nvna_FMIN"]
        if fmax is not None:
            self._fmax = fmax
        else:
            self._fmax = nvna_constants["nvna_FMAX"]
        if n_pts is not None:
            self._npts = n_pts
        else:
            self._npts = nvna_constants["nvna_NptsMAX"]
        # perform SOL measurements
        input("Plug SHORT termination to PORT1 and press Enter")
        S11_short_all = np.zeros((n_average, self._npts), dtype=np.complex128)
        for k in range(n_average):
            freq, S11_short = self.get_S11(self._fmin, self._fmax, self._npts)
            S11_short_all[k, :] = S11_short
        input("Plug OPEN termination to PORT1 and press Enter")
        S11_open_all = np.zeros((n_average, self._npts), dtype=np.complex128)
        for k in range(n_average):
            _, S11_open = self.get_S11(self._fmin, self._fmax, self._npts)
            S11_open_all[k, :] = S11_open
        input("Plug 50Ohm termination to PORT1 and press Enter")
        S11_50_all = np.zeros((n_average, self._npts), dtype=np.complex128)
        for k in range(n_average):
            _, S11_50 = self.get_S11(self._fmin, self._fmax, self._npts)
            S11_50_all[k, :] = S11_50
        # store for future use
        self._frequencies = freq
        self._S11_SHORT = np.average(S11_short_all, axis=0)
        self._S11_OPEN = np.average(S11_open_all, axis=0)
        self._S11_LOAD = np.average(S11_50_all, axis=0)
        # convert to impedance
        self._Z_SHORT = S2Z(self._S11_SHORT)
        self._Z_OPEN = S2Z(self._S11_OPEN)
        self._Z_LOAD = S2Z(self._S11_LOAD)
        self._1PCAl = True
        if savecal:
            self.save_1PCal()

    def PORT1_measurement(self, de_embed_fun=None, convert_fun=None, N_average=6):
        """method for PORT1 end user interface

        Args:
            de_embed_fun (_type_, optional): _description_. Defaults to None.
            convert_fun (_type_, optional): _description_. Defaults to None.
        """
        S11_measured_all = np.zeros((N_average, self._npts), dtype=np.complex128)
        for i in range(N_average):
            print(f"\t--- Measurement {i+1}/{N_average} ---")
            _, S11_measured = self.get_S11(self._fmin, self._fmax, self._npts)
            S11_measured_all[i, :] = S11_measured
        S11_measured_moy = np.average(S11_measured_all, axis=0)
        self._EMPTY = False
        self._S11 = S11_measured_moy

        return self._frequencies, S11_measured_moy

    def get_last_PORT1_Scattering(self):
        """returns the last S11 measurement

        Returns:
            freq (numpy array): frequencies of measurement
            S11 (numpy array): reflection S parameter
        """
        return self._frequencies, self._S11

    def get_S11_Short(self):
        """returns the S11 short calibration measurement

        Returns:
            freq (numpy array): frequencies of calibration
            S11_S (numpy array): reflection S parameter for short calibration
        """
        return self._frequencies, self._S11_SHORT

    def get_S11_Open(self):
        """returns the S11 open calibration measurement

        Returns:
            freq (numpy array): frequencies of calibration
            S11_O (numpy array): reflection S parameter for open calibration
        """
        return self._frequencies, self._S11_OPEN

    def get_S11_Load(self):
        """returns the S11 load calibration measurement

        Returns:
            freq (numpy array): frequencies of calibration
            S11_L (numpy array): reflection S parameter for load calibration
        """
        return self._frequencies, self._S11_LOAD

    def get_S11_SOL(self):
        """returns the S11 calibrations measurements for the full calibration

        Returns:
            freq (numpy array): frequencies of calibration
            S11_S (numpy array): reflection S parameter for short calibration
            S11_O (numpy array): reflection S parameter for open calibration
            S11_L (numpy array): reflection S parameter for load calibration
        """
        return self._frequencies, self._S11_SHORT, self._S11_OPEN, self._S11_LOAD

    def get_last_PORT1_Impedance(self):
        """returns the last de-embbed Z measurement

        Returns:
            freq (numpy array): frequencies of measurement
            Z (numpy array): impedance
        """
        Z = None
        if self._EMPTY:
            print("Warning: no measurement performed yet")
        else:
            if self._1PCAl or self._FULLCAL:
                if self._Tmode:
                    Z = self.Z_de_embedd(
                        self._S11, self._Z_SHORT, self._Z_OPEN, self._Z_LOAD
                    )
                else:
                    Z = self.Z_de_embedd(
                        self.scattering2impedance(self._S11),
                        self._Z_SHORT,
                        self._Z_OPEN,
                        self._Z_LOAD,
                    )
            else:
                Z = self.scattering2impedance(self._S11)
        return self._frequencies, Z

    def save_last_PORT1_measurement(self, fname):
        """saves the last measurement to a file.
        Scattering parameter is not de-embedded, but impedance is de-embedded

        Args:
            fname (str): filename
        """
        freq, Z = self.get_last_PORT1_Impedance()
        S11 = Z2S(Z)
        save_1Pmeasurement_to_file(fname, freq, S11, Z)
