from serialport import SerialPort
from ms2k import MS2000

import pyvisa

import nidaqmx
from nidaqmx.constants import AcquisitionType

import numpy as np
import matplotlib.pyplot as plt


def task(samp_collect, samp_rate):
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev2/ai0")
        task.timing.cfg_samp_clk_timing(samp_rate, sample_mode = AcquisitionType.FINITE, samps_per_chan = samp_rate)
        data = task.read(samp_collect)
        return (data)


def system(ms2k, pixelnum_x, pixelnum_y, pixelsize, pmt, samp_collect, samp_rate):
    pixelpos_x = 0
    pixelpos_y = 0
    
    data_list = []
    
    for x in range(20):
         print('Calibrating...')
         task(samp_rate)
    
    for j in range(0,pixelnum_y):
        for i in range(0,pixelnum_x):
            ms2k.move(pixelpos_x, pixelpos_y, 0)
            pixelpos_x = pixelpos_x + pixelsize

            pmt.write("SENSe:FUNCtion:ON H10770PA-40")   #turn pmt on

            #collect data
            data = task(samp_collect, samp_rate)
            data_list.append(data)

            pmt.write("SENSe:FUNCtion:OFF H10770PA-40")    #turn pmt off
            #ms2k.wait_for_device()
            
        pixelpos_y = pixelpos_y - pixelsize
        pixelpos_x = 0
        ms2k.move(0, pixelpos_y, 0)
        pixelpos_x = pixelpos_x + pixelsize
      
    return data_list


def rough_integrate(data_matrix, pixelnum_x, pixelnum_y, samp_collect):
    new_matrix = []
    total_pix = pixelnum_x * pixelnum_y
    
    for i in range(0, total_pix):
        point_sum = 0
        for j in range(0, samp_collect):
            point_sum += data_matrix[i][j]
       
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
    if not ms2k.is_open():
        print("Exiting the program...")
        return
    return ms2k

def connect_pmt(instr, gain, bandwidth):
    rm = pyvisa.ResourceManager()
    pmt = rm.open_resource(instr)
    print(pmt.query('*IDN?'))

    pmt.write('INSTrument:SELect GAIN')
    pmt.write('SOURce:VOLTage:LEVel:IMMediate:AMPLitude ' + str(gain))
    pmt.write('SOURce:VOLTage:LEVel:IMMediate:AMPLitude?')
    print('Selected Gain: ' + pmt.read())

    pmt.write('SENSe:FILTer:LPASs:FREQuency ' + str(bandwidth))
    return pmt


def main():
    # scan system for com ports
    print(f"COM Ports: {MS2000.scan_ports()}")
    
    ms2k = connect_stage("COM3", 115200)

    pmt2100 = connect_pmt('USB::0x1313::0x2F00::00AH0754::0::INSTR', 0.5, 250)

    pixelnum_x = 5   # probably 512x512
    pixelnum_y = 5
    pixelsize = 5   # 0.5 micron
    samp_rate = 10000
    samp_collect = 1000

    data_list = system(ms2k, pixelnum_x, pixelnum_y, pixelsize, pmt2100, samp_rate)

    final_matrix = rough_integrate(data_list, pixelnum_x, pixelnum_y, samp_collect, samp_rate)

    print(final_matrix)

    image_plot(final_matrix)

    # close the serial port
    ms2k.disconnect_from_serial()


if __name__ == "__main__":
    main()
