printk-timestamp-formatter
==========================

Utilities to view kmsg/printk/dmesg timestamps in local time and date, UTC, or epoch seconds, which account for drift.

The printk clock drifts, often a lot, from the local clock (the one ntp feeds). This can cause radically different and incorrect values if directly converted (like with dmesg -T available on some dmesg). This application supports noting and marking drift and using that to calculate much more accurate timestamps.


Applications
------------


**dmesg_format_dates** - This application runs "dmesg" (or you can pipe in a pre-recorded dmesg, e.g. from logs) and uses the calculated drifts to derive accurate timestamps. If outside of the threshold (default 12000 seconds), a new drift marker will be added.


**printk_time_convert** - This application takes a single timestamp and converts it to either a local ctime, utc ctime, or epoch timestamp. It will add a drift note if a recent one is not available.

TODO: Finish documentation


**How can I configure my kmsg to log timestamps?**

Set the value of /sys/module/printk/parameters/time to "Y" (e.x. echo "Y" > /sys/module/printk/parameters/time)


Sample
------

Here is a sample showing the inaccuracies that can creep in:


*First, show that dmesg can't handle the printk drift*

	[media@silverslave printk-timestamp-formatter]$ date; sudo bash -c 'echo "Hello World" > /dev/kmsg'; dmesg -T | grep 'Hello World' | tail -n1

	Wed Sep  9 01:13:56 EDT 2015

	[Wed Sep  9 01:14:31 2015] Hello World


*Next, show that dmesg_format_dates does work with the printk drifts*

	[media@silverslave printk-timestamp-formatter]$ date; sudo bash -c 'echo "Hello World" > /dev/kmsg'; ./dmesg_format_dates | grep 'Hello World' | tail -n1

	Wed Sep  9 01:14:11 EDT 2015

	[Wed Sep  9 01:14:11 2015] Hello World


