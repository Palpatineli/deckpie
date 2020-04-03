"""make pyDAQmx task a context manager
"""
import numpy as np
# pylint: disable=import-error
import PyDAQmx
# pylint: enable=import-error

class ADCInput(object):
    """analog input mode nidaq manager"""
    __setup = False
    data = None
    duration = 0
    input = None

    def __init__(self, device: str='cDAQ1Mod1/ai0', frequency: float=1000.0):
        self.device_name = device
        self.frequency = frequency

    def __enter__(self):
        self.input = PyDAQmx.Task()
        self.input.CreateAIVoltageChan(str.encode(self.device_name), b'', PyDAQmx.DAQmx_Val_Cfg_Default, -10.0, 10.0,
                                       PyDAQmx.DAQmx_Val_Volts, None)

    def setup(self, duration: float):
        self.duration = duration
        total_sample_no = int(round(duration * self.frequency))
        self.input.CfgSampClkTiming(b'', self.frequency, PyDAQmx.DAQmx_Val_Rising, PyDAQmx.DAQmx_Val_FiniteSamps,
                                    np.uint64(total_sample_no))
        self.__setup = True
        self.data = np.zeros((total_sample_no,), dtype=np.float64)

    def run(self):
        if not self.__setup:
            raise IOError("ADCInput no set up")
        self.input.StartTask()
        read_size = PyDAQmx.int32()
        self.input.ReadAnalogF64(-1, -1, PyDAQmx.DAQmx_Val_GroupByChannel, self.data, len(self.data),
                                 PyDAQmx.byref(read_size), None)
        assert read_size == len(self.data)
        return self.data
