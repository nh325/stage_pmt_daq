from ms2k import MS2000

import pyvisa

import nidaqmx
#from nidaqmx.constants import AcquisitionType


def system(ms2k, pixelnum_x, pixelnum_y, pixelsize, pmt, samp_rate):
    pixelpos_x = 0
    pixelpos_y = 0
    ms2k.move(0, 0, 0)
    
    data_matrix = []

    for j in range(0,pixelnum_y):
        for i in range(0,pixelnum_x):
            pixelpos_x = pixelpos_x + pixelsize
            pmt.write("SENSe:FUNCtion:ON H10770PA-40")   #turn pmt on
            ms2k.move(pixelpos_x, pixelpos_y, 0)
            
            #collect data
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan("Dev2/ai0")
                task.timing.cfg_samp_clk_timing(samp_rate)
                data = task.read(samp_rate) 
                data_matrix[i][j].append(data)
                print(data)
                
            pmt.write("SENSe:FUNCtion:OFF H10770PA-40")    #turn pmt off
            #ms2k.wait_for_device()
            
        pixelpos_y = pixelpos_y - pixelsize
        pixelpos_x = 0
        ms2k.move(0, pixelpos_y, 0)
        #/ms2k.wait_for_device() #find better delay (too slow)

def connect_stage(com, baud_rate):
    ms2k = MS2000(com, baud_rate)
    ms2k.connect_to_serial()
    if not ms2k.is_open():
        print("Exiting the program...")
        return
    return ms2k

def connect_pmt(instr):
    rm = pyvisa.ResourceManager()
    pmt2100 = rm.open_resource(instr)
    pmt2100.query('*IDN?')
    return pmt2100


def main():
    # scan system for com ports
    print(f"COM Ports: {MS2000.scan_ports()}")
    
    ms2k = connect_stage("COM3", 115200)

    pmt2100 = connect_pmt('USB::0x1313::0x2F00::00AH0754::0::INSTR')

    pixelnum_x = 10   # probably 512x512
    pixelnum_y = 10
    pixelsize = 5   # 0.5 micron
    samp_rate = 10000

    system(ms2k, pixelnum_x, pixelnum_y, pixelsize, pmt2100, samp_rate)

 
    # close the serial port
    ms2k.disconnect_from_serial()


if __name__ == "__main__":
    main()
