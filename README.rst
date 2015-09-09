printk-timestamp-formatter
==========================

Utilities to view kmsg/printk/dmesg timestamps in local time and date or UTC which account for drift.

The printk clock drifts, often a lot, from the local clock (the one ntp feeds). This can cause radically different and incorrect values if directly converted (like with dmesg -T available on some dmesg). This application supports noting and marking drift and using that to calculate much more accurate timestamps.


Applications
------------


**dmesg_format_dates** - This application runs "dmesg" (or you can pipe in a pre-recorded dmesg, e.g. from logs) and uses the calculated drifts to derive accurate timestamps. If outside of the threshold (default 12000 seconds), a new drift marker will be added.


**printk_time_convert** - This application takes a single timestamp and converts it to either a local ctime, utc ctime, or epoch timestamp. It will add a drift note if a recent one is not available.

TODO: Finish documentation
