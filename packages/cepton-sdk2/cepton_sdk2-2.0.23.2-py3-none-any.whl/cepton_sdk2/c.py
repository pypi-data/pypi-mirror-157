# Raw C interface through the CDLL library
import os
import sys
import platform
import ctypes


def c_struct_to_dict(c_obj, excludes):
    data = {}
    for field in c_obj._fields_:
        name = field[0]
        if(not name): continue
        if (name in excludes): continue
        data[name] = getattr(c_obj, name)
    return data


# Supported platform-machine combinations
#  win32-x64
#  linux-x64, linux-arm64 (NVIDIA Jetson)
#  darwin-x64, darwin-arm64
__machine_lookup = {
    'AMD64': 'x64',
    'x86_64': 'x64',
    'aarch64': 'arm64',
}

__platform_lookup = {

}

def _load_sdk():
    name = 'cepton_sdk2'
    # Find platform
    mach = platform.machine()
    if (mach in __machine_lookup): mach = __machine_lookup[mach]
    # Find arch
    pl = sys.platform
    if (pl in __platform_lookup): pl = __platform_lookup[pl]

    if pl == 'linux':
        lib_name = "lib{}.so".format(name)
    elif pl == 'darwin':
        lib_name = "lib{}.dylib".format(name)
    elif pl == 'win32':
        lib_name = "{}.dll".format(name)
    else:
        raise NotImplementedError("Platform not supported!")
    lib_dir = "lib/{}-{}/".format(pl, mach)

    # Try local and global search paths
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(parent_dir, lib_dir, lib_name)
    if not os.path.exists(path):
        path = lib_name
    print("LOADING ", path)
    return ctypes.CDLL(path)

# =====================
# Refer to cepton_sdk2.h
#
CEPTON_API_VERSION = 203

lib = _load_sdk()

GetErrorCodeName = lib.CeptonGetErrorCodeName
GetErrorCodeName.restype = ctypes.c_char_p

GetSdkVersion = lib.CeptonGetSdkVersion

SensorHandle = ctypes.c_uint64

SensorErrorCallback = ctypes.CFUNCTYPE(None, SensorHandle, ctypes.c_int, ctypes.c_char_p, \
    ctypes.c_void_p, ctypes.c_size_t)

Initialize = lib.CeptonInitialize
Deinitialize = lib.CeptonDeinitialize
StartNetworking = lib.CeptonStartNetworking
StartNetworkingOnPort = lib.CeptonStartNetworkingOnPort
StartNetworkingMulticast = lib.CeptonStartNetworkingMulticast
StartNetworkingMulticast.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint16]
StopNetworking = lib.CeptonStopNetworking

ReplayHandle =ctypes.c_void_p 

ReplayLoadPcap = lib.CeptonReplayLoadPcap
ReplayLoadPcap.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ReplayHandle)]

ReplayUnloadPcap = lib.CeptonReplayUnloadPcap
ReplayPlay = lib.CeptonReplayPlay
ReplayPlayToFinish = lib.CeptonReplayPlayToFinish
ReplayPause = lib.CeptonReplayPause
ReplayGetLength = lib.CeptonReplayGetLength
ReplaySeek = lib.CeptonReplaySeek
ReplayGetSeekPosition = lib.CeptonReplayGetSeekPosition
ReplayNextFrame = lib.CeptonReplayNextFrame
ReplaySetSpeed = lib.CeptonReplaySetSpeed
ReplayGetSpeed = lib.CeptonReplayGetSpeed
ReplayGetIndexPosition = lib.CeptonReplayGetIndexPosition
ReplayIsFinished = lib.CeptonReplayIsFinished
ReplayIsPaused = lib.CeptonReplayIsPaused

StartAsyncRelay = lib.CeptonStartAsyncRelay
StopAsyncRelay = lib.CeptonStopAsyncRelay

ReceiveData = lib.CeptonReceiveData

ParserCallback = ctypes.CFUNCTYPE(ctypes.c_int, SensorHandle, ctypes.c_int64, ctypes.c_void_p, \
    ctypes.c_size_t, ctypes.c_void_p)
RegisterParser = lib.CeptonRegisterParser
UnregisterParser = lib.CeptonUnregisterParser

class SDKFrameArray(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.POINTER(ctypes.c_int16)),
        ('y', ctypes.POINTER(ctypes.c_uint16)),
        ('z', ctypes.POINTER(ctypes.c_int16)),
        ('reflectivities', ctypes.POINTER(ctypes.c_uint8)),
        ('timestamps', ctypes.POINTER(ctypes.c_size_t)),
        ('channel_ids', ctypes.POINTER(ctypes.c_uint8)),
        ('flags', ctypes.POINTER(ctypes.c_uint8)),
        ('handle', ctypes.POINTER(SensorHandle))
    ]
class SdkSensor(ctypes.Structure):
    _fields_ = [
        ('info_size', ctypes.c_uint32),
        ('serial_number', ctypes.c_uint32),
        ('handle', SensorHandle),
        ('model_name', ctypes.c_char*28),
        ('model', ctypes.c_uint16),
        ('', ctypes.c_uint16), # model_reserved
        ('part_number', ctypes.c_uint32),
        ('firmware_version', ctypes.c_uint32),
        ('power_up_timestamp', ctypes.c_int64),
        ('time_sync_offset', ctypes.c_int64),
        ('time_sync_drift', ctypes.c_int64),
        ('return_count', ctypes.c_uint8),
        ('channel_count', ctypes.c_uint8),
        ('', ctypes.c_uint8*2),
        ('status_flags', ctypes.c_uint32),
    ]

    def to_dict(self):
        d = c_struct_to_dict(self, ['info_size', 'model_name', 'status_flags'])
        d['model_name'] = self.model_name.decode('utf8')
        # Add status flags
        # CEPTON_SENSOR_PTP_CONNECTED = 1,
        # CEPTON_SENSOR_PPS_CONNECTED = 2,
        # CEPTON_SENSOR_NMEA_CONNECTED = 4,
        fl = self.status_flags
        d['status_ptp_connected'] = (fl & 1) != 0
        d['status_pps_connected'] = (fl & 2) != 0
        d['status_nmea_connected'] = (fl & 4) != 0
        return d

GetSensorCount = lib.CeptonGetSensorCount
GetSensorInformationByIndex = lib.CeptonGetSensorInformationByIndex
GetSensorInformation = lib.CeptonGetSensorInformation

PointsCallback = ctypes.CFUNCTYPE(None, SensorHandle, ctypes.c_int64, ctypes.c_size_t, \
    ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p)
ListenPoints = lib.CeptonListenPoints
UnlistenPoints = lib.CeptonUnlistenPoints
ListenFrames = lib.CeptonListenFrames
ListenFrames.argtypes = [ctypes.c_int, PointsCallback, ctypes.c_void_p]
UnlistenFrames = lib.CeptonUnlistenFrames
UnlistenFrames.argtypes = [PointsCallback, ctypes.c_void_p]

SerialReceiveCallback = ctypes.CFUNCTYPE(None, SensorHandle, ctypes.c_char_p, ctypes.c_void_p)
ListenSerialLines = lib.CeptonListenSerialLines
UnlistenSerialLines = lib.CeptonUnlistenSerialLines

SensorInfoCallback = ctypes.CFUNCTYPE(None, SensorHandle, ctypes.POINTER(SdkSensor), ctypes.c_void_p)
ListenSensorInfo = lib.CeptonListenSensorInfo
UnlistenSensorInfo = lib.CeptonUnlistenSensorInfo

EnableLegacyTranslation = lib.CeptonEnableLegacyTranslation
DisableLegacyTranslation = lib.CeptonDisableLegacyTranslation

EnableFrameFifo = lib.CeptonEnableFrameFifo
EnableFrameFifo.argtypes = [ctypes.c_int, ctypes.c_int]

DisableFrameFifo = lib.CeptonDisableFrameFifo

FrameFifoFillArray = lib.CeptonFrameFifoFillArray
FrameFifoFillArray.argtypes = [ctypes.POINTER(SDKFrameArray), ctypes.c_uint]

FrameFifoPeekFrameNumPoints = lib.CeptonFrameFifoPeekFrameNumPoints
FrameFifoPeekFrameNumPoints.argtypes = [ctypes.c_uint]

FrameFifoPutBack = lib.CeptonFrameFifoPutBack
FrameFifoRelease = lib.CeptonFrameFifoRelease
FrameFifoEmpty = lib.CeptonFrameFifoEmpty
FrameFifoSize = lib.CeptonFrameFifoSize
FrameFifoFull = lib.CeptonFrameFifoFull

# Service for sdk.py
byref = ctypes.byref
