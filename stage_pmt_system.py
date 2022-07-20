from serialport import SerialPort
from ms2k import MS2000

import pyvisa

import nidaqmx
from nidaqmx.constants import AcquisitionType

import numpy as np
import matplotlib.pyplot as plt


# def task(samp_collect, samp_rate):
#     with nidaqmx.Task() as task:
#         task.ai_channels.add_ai_voltage_chan("Dev2/ai0")
#         task.timing.cfg_samp_clk_timing(samp_rate, sample_mode = AcquisitionType.FINITE, samps_per_chan = samp_collect +1 )
#         data = task.read(samp_collect)
#         return (data)


def system(ms2k, pixelnum_x, pixelnum_y, pixelsize, samp_collect, samp_rate):
    pixelpos_x = 0
    pixelpos_y = 0
    
    data_list = []
    
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev2/ai0")
        
        print('Calibrating...')
        for x in range(200):
            task.timing.cfg_samp_clk_timing(samp_rate, sample_mode = AcquisitionType.FINITE, samps_per_chan = samp_collect +1 )
            task.read(samp_collect)
        
        print('Collecting Data...')
        for j in range(pixelnum_y):
            for i in range(pixelnum_x):
                
                ms2k.move(pixelpos_x, pixelpos_y, 0)
                pixelpos_x = pixelpos_x + pixelsize

                #collect data
                task.timing.cfg_samp_clk_timing(samp_rate, sample_mode = AcquisitionType.FINITE, samps_per_chan = samp_collect +1 )
                data = task.read()
                
                data_list.append(data)
                
            pixelpos_y = pixelpos_y - pixelsize
            pixelpos_x = 0
            ms2k.move(0, pixelpos_y, 0)
            print(str(pixelpos_y * -1) + '/' + str(pixelnum_y * pixelsize))   #progress
        
    return data_list

def rough_integrate(data_matrix, pixelnum_x, pixelnum_y, samp_collect):
    new_matrix = []
    total_pix = pixelnum_x * pixelnum_y
    
    for i in range(0, total_pix):
        point_sum = 0
        for j in range(0, samp_collect):
            point_sum += data_matrix[i][j]
                 
        point_sum = point_sum * 100 / samp_collect
        new_matrix.append(point_sum)
    
    final_matrix = np.reshape(new_matrix, (pixelnum_y, pixelnum_x))
    return final_matrix

def image_plot(matrix):
    plt.figure(1)
    plt.imshow(matrix, interpolation='nearest')
    plt.colorbar()
    plt.grid(True)

    plt.figure(2)
    plt.imshow(matrix, interpolation='bilinear')
    plt.colorbar()
    plt.grid(True)

    plt.figure(3)
    plt.imshow(matrix, interpolation='bicubic')
    plt.colorbar()
    plt.grid(True)

    plt.show()  


def connect_stage(com, baud_rate):
    ms2k = MS2000(com, baud_rate)
    ms2k.connect_to_serial()
    ms2k.set_max_speed('x', 100000)
    ms2k.set_max_speed('y', 100000)

    if not ms2k.is_open():
        print("Exiting the program...")
        return
    return ms2k

def configure_pmt(gain, bandwidth):
    rm = pyvisa.ResourceManager()
    pmt = rm.open_resource('USB::0x1313::0x2F00::00AH0754::0::INSTR')
    pmt.write("SENSe:FUNCtion:STATe? H10770PA-40")
    if int(pmt.read()) != 1:
        print('Turn PMT ON for 30 minutes') 
        return False
    
    print('Connected to ' + pmt.query('*IDN?')
    pmt.write('INSTrument:SELect GAIN')
    pmt.write('SOURce:VOLTage:LEVel:IMMediate:AMPLitude ' + str(gain))
    pmt.write('SOURce:VOLTage:LEVel:IMMediate:AMPLitude?')
    print('Selected Gain: ' + pmt.read())

    pmt.write('SENSe:FILTer:LPASs:FREQuency ' + str(bandwidth))
    return False


def main():
    # scan system for com ports
    print(f"COM Ports: {MS2000.scan_ports()}")
    
    pixelnum_x = 100   # probably 512x512
    pixelnum_y = 100
    pixelsize = 5   # 0.5 micron
    samp_rate = 1000000   #control speed in general
    samp_collect = 1   #how many points
    
    ms2k = connect_stage("COM3", 115200)

    if configure_pmt(0.6, 250):

        data_list = system(ms2k, pixelnum_x, pixelnum_y, pixelsize, samp_collect, samp_rate)

        final_matrix = rough_integrate(data_list, pixelnum_x, pixelnum_y, samp_collect)

        print(final_matrix)

        image_plot(final_matrix)

    # close the serial port
    ms2k.disconnect_from_serial()
    #pmt.write("SENSe:FUNCtion:OFF H10770PA-40")


if __name__ == "__main__":
    main()
