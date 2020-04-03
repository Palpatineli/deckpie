"""interfacing with NIDAQ DAC board, and autocalibrate diode input
author: mail@keji.li
"""

from setuptools import setup

setup(
    name='deckpie',
    version='0.1',
    requires=['PyDAQmx', 'numpy', 'scipy'],
    packages=[],
    package_dir={},
    entry_points={'console_scripts': ['diode_calibrate=deckpie.main:auto']},
    url='',
    license='',
    author='Keji Li',
    author_email='user@keji.li',
    description='convenience functions to treat analog NIDAQ inputs'
)
