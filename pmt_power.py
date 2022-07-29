import pyvisa

def pmt_on():
    rm = pyvisa.ResourceManager()
    pmt = rm.open_resource('USB::0x1313::0x2F00::00AH0754::0::INSTR')
    pmt.write("SENSe:FUNCtion:ON H10770PA-40")
    pmt.write("SENSe:FUNCtion:STATe? H10770PA-40")
    print(pmt.read())

    if int(pmt.read()) != 1:
        print('PMT did not turn on')
        pmt.write('SENSe:CURRent:DC:PROTection:TRIPped?')
        if pmt.read() == 1:
            pmt.write('SENSe:CURRent:DC:PROTection:CLEar')
            pmt.write('SENSe:CURRent:DC:PROTection:TRIPped?')
            if pmt.read() == 0:
                pmt.write("SENSe:FUNCtion:ON H10770PA-40")
    else:
        print("PMT turned on")

def pmt_off():
    rm = pyvisa.ResourceManager()
    pmt = rm.open_resource('USB::0x1313::0x2F00::00AH0754::0::INSTR')
    pmt.write("SENSe:FUNCtion:OFF H10770PA-40")

    pmt.write("SENSe:FUNCtion:STATe? H10770PA-40")

    if int(pmt.read()) != 0:
        print('PMT did not turn off')     
    else:
        print("PMT turned off")
        
def check_pmt_trip():
    rm = pyvisa.ResourceManager()
    pmt = rm.open_resource('USB::0x1313::0x2F00::00AH0754::0::INSTR')
    pmt.write('SENSe:CURRent:DC:PROTection:TRIPped?')
    pmt.read()
    if int(pmt.read()) == 1:
        print('Pmt Tripped')
        pmt.write('SENSe:CURRent:DC:PROTection:CLEar')
        pmt.write('SENSe:CURRent:DC:PROTection:TRIPped?')
        if int(pmt.read()) == 0:
            print('Trip cleared')
    elif int(pmt.read()) == 0:
        print('No trip')

def check_pmt_power():
    rm = pyvisa.ResourceManager()
    pmt = rm.open_resource('USB::0x1313::0x2F00::00AH0754::0::INSTR')

    pmt.write("SENSe:FUNCtion:STATe? H10770PA-40")

    if int(pmt.read()) == 0:
        print('PMT is off')     
    elif int(pmt.read()) == 1:
        print("PMT is on")


#check_pmt_trip()
check_pmt_power()
#pmt_on()

#pmt_off()
