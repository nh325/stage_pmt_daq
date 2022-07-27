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
    '''
    Returns a 2D matrix. Each row represents a pixel, column represents collected data per pixel. 
    Script moves the stage synchronized with DAQ data collection.

    PARAMETERS
    ms2k: stage Object
    pixelnum_x: int number of wanted pixels in the x direction
    pixelnum_y: int number of wanted pixels in the y direction
    pixelsize: int stage movement distance in 0.1 microns. ex) pixel is about 0.5 microns = 5 units 
    samp_collect: int number of samples to collect per pixel
    samp_rate: int speed of sample collection in samples/second
    '''
    #starting absolute position
    pixelpos_x_i = -2000000
    pixelpos_x = -2000000
    pixelpos_y = 0
    ms2k.move(pixelpos_x, pixelpos_y, 0)
    ms2k.wait_for_device()

    #data collection delay for calibration
    calibrate = 200

    total_samps = pixelnum_x * pixelnum_y + calibrate
    data_matrix = []
    
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("Dev2/ai0")
        task.timing.cfg_samp_clk_timing(samp_rate, sample_mode = AcquisitionType.FINITE, samps_per_chan = total_samps)
        task.start()
        
        print('Calibrating...')
        for x in range(calibrate):
            task.read()
        
        print('Collecting Data...')
        for j in range(pixelnum_y):
            for i in range(pixelnum_x):
                
                ms2k.move(pixelpos_x, pixelpos_y, 0)
                ms2k.wait_for_device()
                pixelpos_x = pixelpos_x + pixelsize

                #collect data
                data = task.read(samp_collect)
                data_matrix.append(data)
                
            pixelpos_y = pixelpos_y + pixelsize
            pixelpos_x = pixelpos_x_i
            ms2k.move(pixelpos_x_i, pixelpos_y, 0)
            ms2k.wait_for_device()
            print(str(int((pixelpos_y/pixelsize))) + '/' + str(pixelnum_y) + ' rows acquired')  #just for progress
        
        task.stop()
        
    return data_matrix

def rough_integrate(data_matrix, pixelnum_x, pixelnum_y):
    '''
    Returns 2D matrix with index representing each pixel's xy position. Each value represents intensity at given pixel.
    Sums all the data points per pixel, and divides in ratio to number of data points for consistency with higher number of sample collection.
    Reshapes list of values to wanted x by y matrix
    
    PARAMETERS
    data_matrix: list of lists of sample collection per pixel (not in xy array)
    pixelnum_x: int number of wanted pixels in the x direction
    pixelnum_y: int number of wanted pixels in the y direction
    '''
    new_matrix = []
    total_pix = pixelnum_x * pixelnum_y
    samp_collect = len(data_matrix[0])

    for i in range(0, total_pix):
        point_sum = 0
        for j in range(0, samp_collect):
            point_sum += data_matrix[i][j]
                 
        point_sum = point_sum * 100 / samp_collect
        new_matrix.append(point_sum)
    
    final_matrix = np.reshape(new_matrix, (pixelnum_y, pixelnum_x))
    return final_matrix

def image_plot(matrix):
    '''
    Plots matrix and shows opo up window of graph. Imaging of pixel intensity.
    PARAMTERS
    matrix: 2D matrix (list of list)
    '''
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

def configure_pmt(gain, bandwidth):
    rm = pyvisa.ResourceManager()
    pmt = rm.open_resource('USB::0x1313::0x2F00::00AH0754::0::INSTR')
    pmt.write("SENSe:FUNCtion:STATe? H10770PA-40")
    if int(pmt.read()) != 1:
        print('Turn PMT ON for 30 minutes!!') 
        return False

    print('Connected to ' + pmt.query('*IDN?'))

    pmt.write('INSTrument:SELect GAIN')
    pmt.write('SOURce:VOLTage:LEVel:IMMediate:AMPLitude ' + str(gain))
    pmt.write('SOURce:VOLTage:LEVel:IMMediate:AMPLitude?')
    print('Selected Gain: ' + pmt.read())

    pmt.write('SENSe:FILTer:LPASs:FREQuency ' + str(bandwidth))
    return True

def main():
    
    pixelnum_x = 100   # probably 512x512
    pixelnum_y = 100
    pixelsize = 5   # 0.5 micron
    samp_rate = 1000000   #control speed in general
    samp_collect = 1   #how many points

    ms2k = connect_stage("COM3", 115200)

    if configure_pmt(0.6, 250):

        data_list = system(ms2k, pixelnum_x, pixelnum_y, pixelsize, samp_collect, samp_rate)

        final_matrix = rough_integrate(data_list, pixelnum_x, pixelnum_y)

        print(final_matrix)
        image_plot(final_matrix)

    # close the serial port
    ms2k.disconnect_from_serial()

if __name__ == "__main__":
    main()
