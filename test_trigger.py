import nidaqmx
import numpy as np
import matplotlib.pyplot as plt
from nidaqmx.stream_writers import AnalogMultiChannelWriter
from nidaqmx.stream_writers import AnalogSingleChannelWriter
from nidaqmx.stream_readers import AnalogSingleChannelReader
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import Edge

samp_rate = 10000
samp_collect = 25000
total_pixels = 10

# x = np.arange(samp_rate)
# y = [np.sin(2*np.pi*f * (i/samp_rate)) for i in x]
# y_new = np.tile(y,1)


outputData = []
for i in range(total_pixels+1):
    for i in range(200):
        outputData = np.append(outputData, 10)
    for i in range(200):
        outputData = np.append(outputData, -10)


#outputData = outputData.reshape((3, len(outputX)))

inputData = np.zeros(samp_collect * total_pixels)
#inputData = inputData.reshape((25000, 3))

with nidaqmx.Task() as task_in, nidaqmx.Task() as task_out:
    task_in.ai_channels.add_ai_voltage_chan("Dev2/ai0")
    task_in.timing.cfg_samp_clk_timing(samp_rate, sample_mode = AcquisitionType.FINITE, samps_per_chan = samp_collect * total_pixels)

    task_out.ao_channels.add_ao_voltage_chan('Dev2/ao0')
    task_out.timing.cfg_samp_clk_timing(samp_rate, sample_mode = AcquisitionType.FINITE, samps_per_chan = total_pixels)
    
    task_in.triggers.start_trigger.cfg_dig_edge_start_trig('/Dev2/ao0/StarTrigger', trigger_edge = Edge.RISING)
    writer = AnalogSingleChannelWriter(task_out.out_stream)
    reader = AnalogSingleChannelReader(task_in.in_stream)
    
    writer.write_many_sample(outputData)
    task_out.start()
    task_in.start()

    data = reader.read_many_sample(inputData)

    print(inputData)
    task_in.wait_until_done()
    task_out.wait_until_done()

    plt.plot(inputData)
    plt.show() 
