# printk-timestamp-formatter
Utilities to view kmsg/printk/dmesg timestamps in local time and date, UTC, or epoch seconds, which **account for drift.**

The printk clock drifts, often a lot, from the local clock (the one ntp feeds). This can cause radically different and incorrect values if directly converted (like with dmesg -T available on some dmesg). This application supports noting and marking drift and using that to calculate much more accurate timestamps.


Why not "dmesg -T"
------------------

As noted, dmesg -T is the same as dmesg\_format\_dates --drift=0  and become inaccurate over time, because the tick clock is affected by frequency scaling etc.

Thus, it is recommended to have a cron job that runs *printk\_mark\_drift* as described below, maybe on half-day intervals to keep things accurate. More or less depending on precision desired and average drift of system.

You can use the *dmesg\_get\_drifts* application to show all current marked drifts to gauge how inaccurate your systems clock is


Sample
------

Here is a sample showing the inaccuracies that can creep in:

First, show that dmesg can't handle the printk drift

	[cmd]$ date; sudo bash -c 'echo "Hello World" > /dev/kmsg'; dmesg -T | grep 'Hello World' | tail -n1
	Wed Sep  9 01:13:56 EDT 2015
	[Wed Sep  9 01:14:31 2015] Hello World

Next, show that dmesg\_format\_dates does work with the printk drifts

	[cmd]$ date; sudo bash -c 'echo "Hello World" > /dev/kmsg'; ./dmesg_format_dates | grep 'Hello World' | tail -n1
	Wed Sep  9 01:14:11 EDT 2015
	[Wed Sep  9 01:14:11 2015] Hello World


Applications
------------


**dmesg\_format\_dates**

This application runs "dmesg" (or you can pipe in a pre-recorded dmesg, e.g. from logs) and uses the calculated drifts to derive accurate timestamps.


Run this command to output the kernel log replacing the printk timestamps with calculated timestamps (in one of several formats), taking into account drift.


**printk_mark_drift**

Adds a drift marker to the kmsg log. These are used to calculate the drift. The more of these you have, the more accurate your timestamps are within.

You should consider having a cron job mark the log every couple hours to get up-to-the-second accuracy when using dmesg\_format\_dates


**dmesg\_get\_drifts**

This application will show the drifts within the dmesg log (the timestamp, how much the clock has drifted at that point).

Use this to analyize how much your machine is drifting to determine how often you should be marking the drifts (for accurate timestamps)


**printk\_time\_convert**

This application takes a single timestamp and converts it to either a local ctime, utc ctime, or epoch timestamp. It will add a drift note if a recent one is not available.


**How can I configure my kmsg to log timestamps?**

Set the value of /sys/module/printk/parameters/time to "Y" (e.x. echo "Y" > /sys/module/printk/parameters/time)



Module
------

This package provides printk\_timestamp\_converter which is a python module you can use directly.

The pydoc documentation is available here: http://htmlpreview.github.io/?https://github.com/kata198/printk-timestamp-formatter/blob/master/doc/printk_timestamp_converter.html 


