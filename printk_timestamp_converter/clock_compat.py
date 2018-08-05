# Copyright (c) 2018 Tim Savannah under LGPLv3.
# You should have received a copy of this with this distribution as LICENSE

import math
import time

__all__ = ( '_getSystemUptime', 'UPTIME_SIG_DECIMALS')

global UPTIME_SIG_DECIMALS

if hasattr(time, 'clock_gettime'):
    def _getSystemUptime():
        return time.clock_gettime(time.CLOCK_MONOTONIC)

    clockResolution = time.clock_getres(time.CLOCK_MONOTONIC)
else:
    
    import ctypes
    import os
    import sys

    CLOCK_MONOTONIC = 1

    class timespec(ctypes.Structure):
        _fields_ = [
            ('tv_sec', ctypes.c_long),
            ('tv_nsec', ctypes.c_long)
        ]

        def __repr__(self):
            return "tv_sec=%d   tv_nsec=%d" %(self.tv_sec, self.tv_nsec)

    librt = ctypes.CDLL('librt.so.1', use_errno=True)
    clock_gettime = librt.clock_gettime
    clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

    clock_getres = librt.clock_getres
    clock_getres.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

    resTimespec = timespec()
    try:
        ret = clock_getres(CLOCK_MONOTONIC, ctypes.pointer(resTimespec))
        if ret != 0:
            errnoVal = ctypes.get_errno()
            raise OSError('non-zero return on clock_getres and errno is %d: %s' %(errnoVal, os.strerror(errnoVal) ))
        else:
            clockResolution = resTimespec.tv_sec + (resTimespec.tv_nsec * 1e-09)
            print ( repr(clockResolution) )
            
    except Exception as resException:
        sys.stderr.write('Error calling clock_getres: %s  %s\n' %(str(type(resException)), str(resException)))
        clockResolution = 1e-09
    
        

    def _getSystemUptime():
        t = timespec()
        if clock_gettime(CLOCK_MONOTONIC , ctypes.pointer(t)) != 0:
            errno_ = ctypes.get_errno()
            raise OSError(errno_, os.strerror(errno_))
        return t.tv_sec + t.tv_nsec * 1e-9


if int(clockResolution) > 0:
    
    UPTIME_SIG_DECIMALS = 0

else:
    
    UPTIME_SIG_DECIMALS = int(abs(math.log10(clockResolution)))

print ( "Sig decimals: " + str( UPTIME_SIG_DECIMALS ) )
