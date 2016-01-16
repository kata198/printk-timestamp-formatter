#!/usr/bin/env python

from distutils.core import setup

if __name__ == '__main__':

    try:
        with open('README.rst', 'rt') as f:
            long_description = f.read()
    except:
        long_descrption = ''

    setup(name='printk-timestamp-converter',
            version='2.1.1',
            description='Utility for printing dmesg/kmsg/printk timestamps, taking into account drift.',       
            long_description=long_description,
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            maintainer_email='kata198@gmail.com',
            license='LGPLv2',
            packages=['printk_timestamp_converter'],
            scripts=['dmesg_format_dates', 'printk_time_convert'],
    )
