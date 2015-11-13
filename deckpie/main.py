#!/user/bin/env python3
"""record diode signal from National Instrument DAQmx and calculate the correct pixel level to use for OI synchronization
"""
import PyDAQmx
import numpy as np


def list_dev(is_print=True):
    name_buffer = bytes(128)
    PyDAQmx.DAQmxGetSysDevNames(name_buffer, 128)
    names = name_buffer[0:name_buffer.find(b"\x00")].split(b", ")
    for name in names:
        print(name)
    return names


def list_chan(dev_name: bytes):
    name_buffer = bytes(1024)
    PyDAQmx.DAQmxGetDevAIPhysicalChans(bytes(dev_name), name_buffer, 1024)
    names = name_buffer[0:name_buffer.find(b"\x00")].split(b", ")
    for name in names:
        print(name)
    return names


def record(device=b'cDAQ1Mod1/ai0', time=20, frequency=1000.0):
    analog_input = PyDAQmx.Task()
    read = PyDAQmx.int32()
    total_sample_no = round(time * frequency)
    data = np.zeros((total_sample_no,), dtype=np.float64)

    # DAQmx Configure Code
    analog_input.CreateAIVoltageChan(device, b"", PyDAQmx.DAQmx_Val_Cfg_Default, -10.0, 10.0, PyDAQmx.DAQmx_Val_Volts,
                                     None)
    analog_input.CfgSampClkTiming(b"", frequency, PyDAQmx.DAQmx_Val_Rising, PyDAQmx.DAQmx_Val_FiniteSamps,
                                  np.uint64(total_sample_no))
    # Wait for User Input to start
    result = input(
        "NiDaq box ready to run {0}s at {1}Hz. Press Enter to start recording. input (a)bort to quit.".format(time,
                                                                                                              frequency))
    if len(result) > 0 and result[0] == 'a':
        import sys
        sys.exit(0)
    # DAQmx Start Code
    analog_input.StartTask()
    # DAQmx Read Code
    analog_input.ReadAnalogF64(total_sample_no, float(time), PyDAQmx.DAQmx_Val_GroupByChannel, data, total_sample_no,
                               PyDAQmx.byref(read), None)
    print("Recording finished")
    return data


def find_rising_edge(series):
    onset_index = np.logical_and(series[2:] > series[1:-1], series[0:-2] >= series[1:-1])
    onset = (series[1:-1])[onset_index]
    peak_index = np.logical_and(series[2:] <= series[1:-1], series[0:-2] < series[1:-1])
    peak = (series[1:-1])[peak_index]
    assert (len(peak) == len(onset))
    signals = peak - onset
    if len(onset) < 2:
        print("no diode signal detected")
    else:
        print("diode base is {0}, with {1} std".format(onset.mean(), onset.std()))
        print("1/3 strength pixel at {0}, with strength {1}".format(255 - round(len(signals) * (2 / 3)),
                                                                    signals[round(len(signals) / 3)]))
    full_signals = np.zeros((256 - len(signals),))
    full_signals = np.append(full_signals, signals)
    return full_signals
