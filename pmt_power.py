import pyvisa

def pmt_on():
    rm = pyvisa.ResourceManager()
    pmt = rm.open_resource('USB::0x1313::0x2F00::00AH0754::0::INSTR')
    pmt.write("SENSe:FUNCtion:ON H10770PA-40")

    pmt.write("SENSe:FUNCtion:STATe? H10770PA-40")
    print(pmt.read())

    if int(pmt.read()) != 1:
        print('PMT did not turn on')
    else:
        print("PMT turned on")

def pmt_off():
    rm = pyvisa.ResourceManager()
    pmt = rm.open_resource('USB::0x1313::0x2F00::00AH0754::0::INSTR')
    pmt.write("SENSe:FUNCtion:OFF H10770PA-40")

    pmt.write("SENSe:FUNCtion:STATe? H10770PA-40")
    print(pmt.read())

    if int(pmt.read()) != 0:
        print('PMT did not turn off')     
    else:
        print("PMT turned off")

pmt_on()
#pmt_off()
    

