# Copyright (c) 2015, 2016, 2017 Tim Savannah under LGPLv3.
# You should have received a copy of this with this distribution as LICENSE
#
# This provides a library for dealing with printk drift between actual uptime.
#   This will provide a reasonable estimate for recent timestamps, but not a completely accurate picture for all timestamps (can drift by up to an hour in a month's time).
#   For accurate timing, this would need to constantly collect samples.
#   Alternativly, it can use every sample that IS present, and create a set of ranges.

import datetime
import os
import re
import sys
import time
import subprocess

PRINTK_DRIFT_MSG = '=== Detecting printk drift:'
PRINTK_DRIFT_PATTERN = re.compile('^(\[[ ]*)(?P<printk_seconds>[\d]+)[\.][\d]+(\]) (' + PRINTK_DRIFT_MSG + ') (?P<uptime_seconds>[\d]+)' )

PRINTK_WITH_TIME_PATTERN = re.compile('^(\[[ ]*)(?P<printk_seconds>[\d]+)[\.][\d]+(\])')

PRINTK_DRIFT_REDETECT_TIME = 12000 # seconds

__all__ = ('NotRecentEnoughDriftDelta', 'getSystemUptime', 'printk_calculateCurrentDrift' ,'printk_calculateDrifts', 'printk_calculateDrift', 'printk_convertTimestampToDatetime', 'printk_convertTimestampToUTCDatetime', 'printk_convertTimestampToEpoch', 'printk_markCurrentDrift')

__version__ = '3.0.0'
__version_tuple__ = (3, 0, 0)


class NotRecentEnoughDriftDelta(Exception):
    '''
        NotRecentEnoughDriftDelta - Exception raised when a close enough drift market cannot be found, and one cannot be created because you cannot write to /dev/kmsg.
    '''
    pass

def getSystemUptime():
    '''
        getSystemUptime - Gets system uptime in seconds

        @return <int> - Seconds of uptime
    '''
    with open('/proc/uptime', 'r') as procUptime:
        uptime = int(procUptime.read().split('.')[0])
    return uptime
    

defaultEncoding = sys.getdefaultencoding()
if bytes == str:
    # Python 2
    def tostr(x):
        if isinstance(x, unicode):
            return x.encode(defaultEncoding)
        else:
            return str(x)
else:
    # Python 3
    def tostr(x):
        if isinstance(x, bytes) is False:
            return str(x)
        return x.decode(defaultEncoding)

# Drift is measured as printk_seconds - uptime_seconds
def printk_calculateDrifts(dmesgContents=None, onlyLatest=False, maxDriftRedetectTime=PRINTK_DRIFT_REDETECT_TIME, markIfRequired=True):
    '''
        printk_calculateDrifts - Calculates the drifts for a dmesg log

            @param dmesgContents <str/None> Default None - Contents of dmesg, or None to fetch new

            @param onlyLatest  <bool> Default False    - Only fetch the most recent.

            @param maxDriftRedetectTime <int> Default PRINTK_DRIFT_REDETECT_TIME - Number of seconds that represents max tolerance between printk detections. If set to 0, any present
                                                delta is okay.

            @param markIfRequired <bool> default True - if a marker is not found within #maxDriftRedetectTime and this is set to True, a mark will be attempted (requires root and dmesgContents to be None). Otherwise, in the circumstance that there is not a recent enough marker, a NotRecentEnoughDriftDelta will be raised (more info below)

            This will add an entry if one has not been inserted in the last PRINTK_DRIFT_REDIRECT_TIME seconds.
            The entry compares the printk "time" with current uptime, to detect a drift.

            This function returns a dictionary with each line number containing a drift delta to that delta.

            @return dict - key is line number <0-origin> containing a drift delta, and value is that delta. Also an entry "latest" which contains most recent drift, and "earliest" which contains the oldest drift.

            Use these results to apply compounded deltas as you reach different lines in the output, or just use latest for a fuzzier view.

            @raises NotRecentEnoughDriftDelta - If onlyLatest is True and if a close enough sample (within #maxDriftRedetectTime seconds) is not present AND dmesgContents are provided, or a close enough sample is not present and /dev/kmsg is not writeable by current user. Exception message contains what the issue was and is suitable for printing.

            If maxDriftRedetectTime is 0, and there is no given delta, and one cannot be created, a NotRecentEnoughDriftDelta will be raised.

            This starts with a drift of 0 at zero. This could vary, depending on how far out the first delta is placed, and how off the clock was on boot from being corrected later. You may want to ignore this, maybe not. The most accurate option is to add a printk drift marker after ntpdate service on the boot
    '''

    drifts = {0 : 0} # Start with 0 drift. You could disregard this or not, results will vary depending on how far out since boot the first delta note is placed, and how "off" the original clock was at boot. Best option is to place a drift marker in your init,

    procUptime = getSystemUptime()
    
    if dmesgContents is None:
        pipe = subprocess.Popen('dmesg', shell=True, stdout=subprocess.PIPE)
        dmesgContents = tostr(pipe.stdout.read())
        pipe.wait()
        wasPassedContents = False
    else:
        wasPassedContents = True
    
    dmesgContentsSplit = dmesgContents.split('\n')
    dmesgContentsSplit.reverse()

    lineNo = len(dmesgContentsSplit) - 1
    # Search for a recent sample within threshold
    for line in dmesgContentsSplit:
        if PRINTK_DRIFT_MSG in line:
            matchObj = PRINTK_DRIFT_PATTERN.match(line)
            if matchObj is not None:
                groupDict = matchObj.groupdict()
                msgUptimeSeconds = int(groupDict['uptime_seconds'])
                drift = int(groupDict['printk_seconds']) - msgUptimeSeconds 
                if 'latest' not in drifts:
                    if not maxDriftRedetectTime:
                        drifts['earliest'] = drifts['latest'] = drifts[lineNo] = drift
                    elif procUptime - msgUptimeSeconds <  maxDriftRedetectTime:
                        drifts['earliest'] = drifts['latest'] = drifts[lineNo] = drift
                    else:
                        break
                    if onlyLatest is True:
                        return drifts
                else:
                    drifts['earliest'] = drifts[lineNo] = drift
        lineNo -= 1

    if 'latest' in drifts:
        return drifts

    if wasPassedContents is True:
        raise NotRecentEnoughDriftDelta('Cannot calculate printk drift: a close enough sample is not present, and an input was provided. Please run this on the host that provided the file to calculate the current drift. NOTE: There is an issue to where this is only accurate with recent dates due to varying drift.')
        

    # Otherwise, try to get a new one. usually, must be root.
    if markIfRequired:
        try:
            printk_markCurrentDrift()
        except Exception as e:
            raise NotRecentEnoughDriftDelta("Cannot calculate printk drift: a close enough sample is not present. Please retry as root, or another user that can write to /dev/kmsg, after which you can resume unprivileged usage.")
    else:
        raise NotRecentEnoughDriftDelta('Cannot calculate printk drift: a close enough sample is not present and marking has been disabled. Either increase maxDriftRedetectTime (or set to 0), or call with markIfRequired=True when root, or otherwise provide marking.')
    
    # Read contents again, reverse and find the line we just added. Calculate the delta and return
    time.sleep(.001)
    pipe = subprocess.Popen('dmesg', shell=True, stdout=subprocess.PIPE)
    content = tostr(pipe.stdout.read())
    pipe.wait()
    

    lines = content.split('\n')
    lineNo = len(lines) - 1
    while lineNo >= 0:
        line = lines[lineNo]
        if line:
            matchObj = PRINTK_DRIFT_PATTERN.match(line)
            if matchObj is not None:
                groupDict = matchObj.groupdict()
                msgUptimeSeconds = int(groupDict['uptime_seconds'])
                drift = int(groupDict['printk_seconds']) - msgUptimeSeconds 
                drifts['earliest'] = drifts['latest'] = drifts[lineNo] = drift
                return drifts
        lineNo -= 1

    raise NotRecentEnoughDriftDelta('Wrote latest drift but could not find it upon reopening.')

def printk_calculateCurrentDrift(dmesgContents=None, maxDriftRedetectTime=PRINTK_DRIFT_REDETECT_TIME):
    '''
        printk_calculateCurrentDrift - Convienance function for printk_calculateDrifts which just returns the latest drift.

        This function will try to add a new entry if the last delta is outside the given threshold

        @see printk_calculateDrifts

        @return <int> - Latest delta
    '''
    return printk_calculateDrifts(dmesgContents, onlyLatest=True, maxDriftRedetectTime=maxDriftRedetectTime)['latest']

def printk_convertTimestampToEpoch(timestamp, drift=None, uptime=None):
    '''
        printk_convertTimestampToEpoch - Converts a printk timestamp to a "seconds since epoch" time value

        @param timestamp <str/float> - String/Float of the timestamp (e.x. [1234.14])
        @param drift     <float> - Given drift, or None to calculate a drift. If calling often, calculate drift first with printk_calculateDrift(s)
        @param uptime    <int> - Current uptime for calcluation, or None to calculate. If calling often, calcluate first with getSystemUptime

        @return <int> - seconds since epoch. Can be used for a datetime.fromtimestamp
    '''
    timestamp = str(float(timestamp))
    timestamp = int(timestamp.split('.')[0])

    if drift is None:
        drift = printk_calculateCurrentDrift()
    secondsSinceUptime = timestamp - drift

    if uptime is None:
        uptime = getSystemUptime()
    else:
        uptime = int(uptime)

    now = int(time.time())

    msgTime = now - (uptime - secondsSinceUptime)

    return msgTime

def printk_convertTimestampToDatetime(timestamp, drift=None, uptime=None):
    '''
        printk_convertTimestampToDatetime - Converts a printk timestamp to a local datetime object.

        @see printk_convertTimestampToEpoch

        @return - <datetime.datetime> - Datetime object in local time
    '''
    msgTime = printk_convertTimestampToEpoch(timestamp, drift, uptime)
    dateTimeObj = datetime.datetime.fromtimestamp(msgTime)
    return dateTimeObj
    
def printk_convertTimestampToUTCDatetime(timestamp, drift=None, uptime=None):
    '''
        printk_convertTimestampToUTCDatetime - Converts a printk timestamp to a utc datetime object

        @see printk_convertTimestampToEpoch

        @return - <datetime.datetime> - Datetime object in utc time
    '''
    msgTime = printk_convertTimestampToEpoch(timestamp, drift, uptime)
    dateTimeObj = datetime.datetime.utcfromtimestamp(msgTime)
    return dateTimeObj

def printk_markCurrentDrift():
    '''
        printk_markCurrentDrift - Mark the current uptime in kmsg for calcuation of drift. The more often you do this, the more accurate your timestamps in between will be.

        @return - Current uptime in seconds
    '''
    procUptime = getSystemUptime()
    doRaise = False
    kmsgBuff = open('/dev/kmsg', 'w')
    kmsgBuff.write(PRINTK_DRIFT_MSG + ' ' + str(procUptime) + "\n")
    kmsgBuff.close()

    return procUptime

# vim: set sw=4 ts=4 st=4 expandtab
