from serial import Serial
from serial import SerialException
from serial import EIGHTBITS
from serial import PARITY_NONE
from serial import STOPBITS_ONE
from serial.tools import list_ports
from serialport import SerialPort
from ms2k import MS2000


def movement(ms2k, pixelnum, pixelsize):
    pixelpos_x = 0
    pixelpos_y = 0
    ms2k.move(0, 0, 0)
    # move the stage
    for j in range(0,pixelnum):
        for i in range(0,pixelnum):
            pixelpos_x = pixelpos_x + pixelsize
            ms2k.move(pixelpos_x, pixelpos_y, 0)
            ms2k.wait_for_device() #find better delay (too slow)
        pixelpos_y = pixelpos_y - pixelsize
        pixelpos_x = 0
        ms2k.move(0, pixelpos_y, 0)
        ms2k.wait_for_device() #find better delay (too slow)


def main():
    # scan system for com ports
    print(f"COM Ports: {MS2000.scan_ports()}")
 
    # connect to the MS2000
    ms2k = MS2000("COM3", 115200)
    ms2k.connect_to_serial()
    if not ms2k.is_open():
        print("Exiting the program...")
        return

    movement(ms2k, 10, 10000)
    #ms2k.move(0, 0, -100)

    ms2k.wait_for_device()
 
    # close the serial port
    ms2k.disconnect_from_serial()


if __name__ == "__main__":
    main()
  

