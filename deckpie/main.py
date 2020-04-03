#!/user/bin/env python3
"""record diode signal from National Instrument DAQmx and calculate the correct pixel level to use
for OI synchronization
"""
import time
import socket
import atexit
# pylint: disable=import-error
import PyDAQmx
# pylint: enable=import-error
import numpy as np
from . import tcp


def list_dev(is_print=True):
    name_buffer = bytes(128)
    PyDAQmx.DAQmxGetSysDevNames(name_buffer, 128)
    names = name_buffer[0:name_buffer.find(b"\x00")].split(b", ")
    if is_print:
        for name in names:
            print(name)
    return names


def list_chan(dev_name: bytes, is_print=True):
    name_buffer = bytes(1024)
    PyDAQmx.DAQmxGetDevAIPhysicalChans(bytes(dev_name), name_buffer, 1024)
    names = name_buffer[0:name_buffer.find(b"\x00")].split(b", ")
    if is_print:
        for name in names:
            print(name)
    return names


def record(duration: int=20, device: str='cDAQ1Mod1/ai0', frequency: float=1000.0) -> \
        (np.ndarray, (float, float)):
    """record a fixed length waveform from specified device
    Args:
        duration: the total duration of recording in seconds
        device: the nidaq device name, usually is "boardname/channelname", boardname is usually
            cDAQ#[Mod#], and channelname is usually ai#, ao#, di#, or do#
        frequency: sampling frequency of input channels
    Returns:
        (sample time series, (computer start_time, computer, end_time))
    """
    analog_input = PyDAQmx.Task()
    total_sample_no = round(duration * frequency)
    data = np.zeros((total_sample_no,), dtype=np.float64)

    # DAQmx Configure Code
    analog_input.CreateAIVoltageChan(str.encode(device), b"", PyDAQmx.DAQmx_Val_Cfg_Default,
                                     -10.0, 10.0, PyDAQmx.DAQmx_Val_Volts, None)
    analog_input.CfgSampClkTiming(b"", frequency, PyDAQmx.DAQmx_Val_Rising,
                                  PyDAQmx.DAQmx_Val_FiniteSamps, np.uint64(total_sample_no))
    # Wait for User Input to start
    result = input(
        "NiDaq box ready to run {0}s at {1}Hz. Press Enter to start recording. "
        "input (a)bort to quit.".format(duration, frequency))
    if len(result) > 0 and result[0] == 'a':
        import sys
        sys.exit(0)
    start_time = time.time()
    # DAQmx Start Code
    analog_input.StartTask()
    end_time = time.time()
    # DAQmx Read Code
    read_size = PyDAQmx.int32()
    analog_input.ReadAnalogF64(total_sample_no, float(duration), PyDAQmx.DAQmx_Val_GroupByChannel,
                               data, total_sample_no, PyDAQmx.byref(read_size), None)
    print("Recording finished")
    return data, (start_time, end_time)


def diode_test_signal(series):
    diff = np.diff(series)
    onset_index = np.nonzero(np.logical_and(diff[1:] > 0, diff[:-1] <= 0))[0] + 1
    peak_index = np.nonzero(np.logical_and(diff[1:] <= 0, diff[:-1] > 0))[0] + 1
    assert len(peak_index) == len(onset_index)
    assert len(onset_index) > 1, "no diode signal detected"
    return series[peak_index] - series[onset_index]


def time_negotiate(port, min_wait=0.01):
    target_time = float(port.receive())
    wait_time = target_time - time.time()
    if wait_time < min_wait:
        port.send(b'fuck')
    else:
        port.send(b'ok')
    time.sleep(target_time - time.time())


def auto(port_id: int=32):
    import json
    import pkg_resources
    tcp_config = json.load(open(pkg_resources.resource_string('deckpie', 'config.json')))
    print('connecting stimulator...')
    with tcp.TcpServer(tcp_config['client_computer']) as port:
        port.connect()
        print('stimulator connected.')
        while True:
            time_negotiate(port)
