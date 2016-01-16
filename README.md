# printk-timestamp-formatter
Utilities to view kmsg/printk/dmesg timestamps in local time and date, UTC, or epoch seconds, which account for drift.

The printk clock drifts, often a lot, from the local clock (the one ntp feeds). This can cause radically different and incorrect values if directly converted (like with dmesg -T available on some dmesg). This application supports noting and marking drift and using that to calculate much more accurate timestamps.


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

**dmesg_format_dates**

This application runs "dmesg" (or you can pipe in a pre-recorded dmesg, e.g. from logs) and uses the calculated drifts to derive accurate timestamps. If outside of the threshold (default 12000 seconds), a new drift marker will be added, unless you specify a fixed drift.

	dmesg_format_dates (Options) - Formats kernel log (dmesg/kmsg), replacing the uptimes with timestamps, accounting for drift.
		
		
		The kernel logs messages with a timestamp of seconds since boot, which is an independent timesource from standard uptime and clocks, and often drifts by several seconds.

		This program takes account for adjusting time with those drifts. It will add a drift marker if one hasn't been added since a certain threshold (or use the printk_mark_drift program to explicitly add one).

		Timestamps are calculated using the drifts marked. The more you mark, the more accurate your timestamps will be.

		You may either run this program without providing input (in which it will call "dmesg"), or pipe in a kmsg log file/source.

			Options:

				--drift=N               Assume a fixed drift of N, instead of using (or adding) the drift markers.

			Output Formats (pick one):
  
				-l or --local           Output time on LOCAL format (DEFAULT).
				-u or --utc             Output time in UTC format.
				-e or --epoch           Output time in Unix Epoch format (seconds since Jan 1 1970 00:00:00)



**printk_time_convert**

This application takes a single timestamp and converts it to either a local ctime, utc ctime, or epoch timestamp. It will add a drift note if a recent one is not available.

	printk_time_convert (Options) [printk1 timestamp] (optional: additional timestamps)

		Converts printk timestamps, which may be inaccurate, to human readable dates that are accurate.

			Output Formats (pick one):

				 -l or --local           Output time on LOCAL format (DEFAULT).
				-u or --utc             Output time in UTC format.
				-e or --epoch           Output time in Unix Epoch format (seconds since Jan 1 1970 00:00:00)


	For each timestamp given, the conversion will be printed, one per line.


**printk_mark_drift**

Adds a drift marker to the kmsg log. These are used to calculate the drift. The more of these you have, the more accurate your timestamps are within.

	printk_mark_drift
		Marks the current drift between the kernel's uptime and clock time in kmsg log.

		These marks are used to calculate timestamps adjusting for drift in the timesource. The more often this is done, the more accurate timestamps you can get.

**How can I configure my kmsg to log timestamps?**

Set the value of /sys/module/printk/parameters/time to "Y" (e.x. echo "Y" > /sys/module/printk/parameters/time)



Module
------

This package provides printk\_timestamp\_converter which is a module you can use directly.

The pydoc documentation is available here: http://htmlpreview.github.io/?https://github.com/kata198/printk-timestamp-formatter/blob/master/doc/printk_timestamp_converter.html 


