import nidaqmx
import numpy as np
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.stream_writers import AnalogSingleChannelWriter
from nidaqmx.stream_readers import AnalogSingleChannelReader

samp_rate = 1000000
total_samps = 1000
samp_collect = 1000
f = 100

x = np.arange(samp_rate)
y = [np.sin(2*np.pi*f * (i/samp_rate)) for i in x]
y_new = np.tile(y,1)

with nidaqmx.Task() as task_in, nidaqmx.Task() as task_out:
    task_in.ai_channels.add_ai_voltage_chan("Dev2/ai0")
    task_in.timing.cfg_samp_clk_timing(samp_rate, sample_mode = AcquisitionType.FINITE, samps_per_chan = total_samps)

    task_out.ao_channels.add_ao_voltage_chan('Dev2/ao0')
    task_out.timing.cfg_samp_clk_timing(samp_rate, sample_mode = AcquisitionType.FINITE, samps_per_chan = total_samps)
    
    task_in.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev2/ao0/StartTrigger')
    writer = AnalogSingleChannelWriter(task_out.out_stream)
    reader = AnalogSingleChannelReader(task_in.in_stream)
    
    writer.write_many_samples(y_new)
    
    task_in.start()
    task_out.start()
    data = reader.read_may_samples.read(samp_collect)
    task_in.wait_until_done()
    task_out.wait_until_done()