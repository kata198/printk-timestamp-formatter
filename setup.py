#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

if __name__ == '__main__':

    try:
        with open('README.rst', 'rt') as f:
            long_description = f.read()
    except:
        long_descrption = ''

    setup(name='printk-timestamp-converter',
            version='3.0.0',
            description='Utility for printing dmesg/kmsg/printk timestamps, taking into account drift.',       
            long_description=long_description,
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            maintainer_email='kata198@gmail.com',
            url='https://github.com/kata198/printk-timestamp-converter',
            license='LGPLv2',
            packages=['printk_timestamp_converter'],
            keywords=['printk', 'timestamp', 'date', 'convert', 'drift', 'converter', 'dmesg', 'kmsg'],
            scripts=['dmesg_format_dates', 'printk_time_convert', 'printk_mark_drift', 'dmesg_get_drifts'],
            classifiers=['Development Status :: 5 - Production/Stable',
                'Operating System :: POSIX :: Linux',
                'Topic :: System :: Operating System Kernels :: Linux',
            ]
    )
