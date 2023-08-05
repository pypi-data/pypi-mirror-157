import ctypes
from . import c as _c
from .sensor import Sensor
from .frame import Frame


# SDK singleton management object, holds private module variables
class __Sdk:
    cbFrame = None
    cbSensor = None

    # TODO: better handle replay handles
    replayHandle = _c.ReplayHandle()

    @staticmethod
    def error_cb():
        return

class CeptonError(Exception):
    def __init__(self, code=0):
        self.code_name = GetErrorCodeName(code)
        super().__init__(self.code_name)
        self.code = code

def __check(code):
    if (code < 0): raise CeptonError(code)
    #if (code != 0): raise CeptonError(code)


def _sensor_cb(handle, sensor_ptr, user_data):
    d = sensor_ptr[0].to_dict()

    s = Sensor.find_or_create_by_handle(handle)
    s.update_info(d)


def Initialize():
    fn = _c.SensorErrorCallback(__Sdk.error_cb)
    __check(_c.Initialize(_c.CEPTON_API_VERSION, fn))
    __check(_c.EnableLegacyTranslation())
    __Sdk.cbSensor = _c.SensorInfoCallback(_sensor_cb)
    __check(_c.ListenSensorInfo(__Sdk.cbSensor, None))

def Deinitialize():
    __check(_c.UnlistenSensorInfo(__Sdk.cbSensor, None))
    __Sdk.cbSensor = None
    __check(_c.Deinitialize())

def GetErrorCodeName(err: int) -> str:
    return _c.GetErrorCodeName(err).decode('utf8')


def GetVersion() -> str:
    """
    Returns a 3-part or 4-part version string like 2.0.10 or 2.0.10.1
    Only returns 4-part if the last part is non-zero
    """
    v = _c.GetSdkVersion()
    v0 = v & 0xff
    v1 = (v >> 8) & 0xff
    v2 = (v >> 16) & 0xff
    v3 = (v >> 24)
    vs = "{}.{}.{}".format(v0, v1, v2)
    if (v3 != 0): vs += ".{}".format(v3)
    return vs

def StartAsyncRelay(buffers):
    __check(_c.StartAsyncRelay(buffers))

def GetSensorInformation(ind,inf):
    return _c.GetSensorInformationByIndex(ind, inf)

def LoadPcap(pcap: str, **kwargs):
    """Load one pcap
    LoadPcap(pcap, looping=false, speed=100)
    """
    # CEPTON_REPLAY_FLAG_LOAD_WITHOUT_INDEX = 1,
    # CEPTON_REPLAY_FLAG_PLAY_LOOPED = 2,
    # CEPTON_REPLAY_FLAG_LOAD_PAUSED = 4,
    fl = 4 # Paused at load
    speed = kwargs.get('speed', 100)
    if (kwargs.get('looping', False)):
        fl |= 2 # looping
    # TODO: Check kwargs for bad parameters

    # Start of the actual actions
    __check(_c.ReplayLoadPcap(pcap.encode('utf8'), fl,
        _c.byref(__Sdk.replayHandle)))
    if (speed != 100):
        __check(_c.ReplaySetSpeed(__Sdk.replayHandle, speed))
    __check(_c.ReplayPlay(__Sdk.replayHandle))

def ReplayIsFinished():
    return _c.ReplayIsFinished(__Sdk.replayHandle)

def UnloadPcap():
    if __Sdk.replayHandle:
        __check(_c.ReplayUnloadPcap(__Sdk.replayHandle))

def StartNetworking():
    """
    Start listening to sensor network.
    """
    __check(_c.StartNetworking())

def StartNetworkingMulticast(targetMcastGroup, localIf, port):
    __check(_c.StartNetworkingMulticast(targetMcastGroup, localIf, port))

def StopNetworking():
    """
    Stop listening to sensor network.
    """
    __check(_c.StopNetworking())

def EnableFrameFifo(frameMode, nFrames):
    """
    Enable SDK frame FIFO feature.

    Parameters
    ----------
    frameMode : int
        = 0 for natural frame aggregation.
        > 0 for fixed time period in millisecond.
    nFrames : int
        Maximum number of frames in the FIFO.
    """
    assert 0 <= frameMode

    # Convert to us convention in Cepton SDK
    __check(_c.EnableFrameFifo(frameMode * 1000, nFrames))

def DisableFrameFifo():
    __check(_c.DisableFrameFifo())

def FrameFifoGetFrame(timeout):
    """
    Get a cepton_sdk2.Frame instance from the frame FIFO. 

    Parameters
    ----------
    timeout : int
        Maximum time spend on waiting for the next frame. 0 represents 
        wait forever. Larger than 0 represents maximum wait time in 
        millisencond. Function will return a None if timeout.

    Return
    ----------
    A cepton_sdk2.Frame instance or None.
    """
    try:
        length = _c.FrameFifoPeekFrameNumPoints(timeout)
        __check(length)
        # initialize to zeros
        frame = Frame(length)
        sdk_frame = _c.SDKFrameArray()
        #?
        sdk_frame.x = frame.x_raw.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
        sdk_frame.y = frame.y_raw.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16))
        sdk_frame.z = frame.z_raw.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
        sdk_frame.reflectivities = frame.reflectivities_raw.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
        sdk_frame.timestamps = frame.timestamps.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
        sdk_frame.channel_ids = frame.channel_ids.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
        sdk_frame.flags = frame.flags.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
        sdk_frame.handle=frame.handle.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
        __check(_c.FrameFifoFillArray(_c.ctypes.byref(sdk_frame), timeout))
    except CeptonError as e:
        if e.code_name == "CEPTON_ERROR_TIMEOUT":
            return None
        else:
            raise

    frame._finalize()
    return frame

def FrameFifoPutBack():
    __check(_c.FrameFifoPutBack())

def FrameFifoRelease():
    """
    Release the frame. After releasing, the frame won't be accessible.
    """
    __check(_c.FrameFifoRelease())

def FrameFifoEmpty():
    """
    Return
    ----------
    True if FIFO is empty. False if FIFO is not empty.
    """
    ret = _c.FrameFifoEmpty()
    __check(ret)
    return ret > 0

def FrameFifoSize():
    """
    Return
    ----------
    Number of frames in the FIFO.
    """
    ret = _c.FrameFifoSize()
    __check(ret)
    return ret

def FrameFifoFull():
    """
    Return
    ----------
    True if FIFO is full. False if FIFO is not full.
    """
    ret = _c.FrameFifoFull()
    __check(ret)
    return ret > 0