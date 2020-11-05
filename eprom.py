import serial,time #You need the pyserial library
import struct      #For packing data into bytes

print("      ________    _________    _________    _________    _____________ ")
print("    /  ______/|  /  ___   /|  /  ___   /|  /   __   /|  /  _    _    /|")
print("   /  /_____ |/ /  /__/  / / /  /__/  / / /  /  /  / / /  / /  / /  / /")
print("  /  ______/|  /   _____/ / /     ___/ / /  /  /  / / /  / /  / /  / / ")
print(" /  /______|/ /  / _____|/ /  /\  \__|/ /  /__/  / / /  / /  / /  / /  ")
print("/________/|  /__/ /       /__/ /\__/|  /________/ / /__/ /__/ /__/ /   ")
print("|________|/  |__|/        |__|/ |__|/  |________|/  |__|/|__|/|__|/    ")
print("\n")
print("  Allan Gallop 2020")
print("  www.M0VTE.co.uk")
print("  https://github.com/AllanGallop/eprom\n")
print("  Based on work by Robson Couto")
print("  github.com/robsoncouto/eprom\n")


#Default value, 1MB chip:
romsize=1*1024*1024
numsectors=int(romsize/128) # I am sending data in 128 byte chunks
print("Enter COM port address (eg COM1, /dev/ttyACM0)")
comport=str(input(":"))
ser = serial.Serial(comport, 250000, timeout=0) #Serial Port

while True:

    print("  What would you like to do?      ")
    print("                                  ")
    print("          1-Read eprom            ")
    print("          2-burn eprom            ")
    print("          3-wipe eprom            ")
    print("          4-blank check           ")
    print("          5-select chip size      ")
    print("          6-verify eprom          ")
    print("                                  ")
    print("          7-quit                \n")
    #get option from user:
    option=int(input("Please insert a number:"))

    #Read EPROM
    if(option==1):
        name=input("What the name of the file?")

        f = open(name, 'w')
        f.close()
        ser.flushInput()
        ser.write(b"\x55")
        ser.write(bytes("r","ASCII"))
        numBytes=0
        f = open(name, 'ab')
        #I just read the data and put it into a file.
        #TODO - Checksum scheme as when burning
        while (numBytes<romsize):
            while ser.inWaiting()==0:
                print("Reading from eprom. Current porcentage:{:.2%}".format(numBytes/romsize),end='\r')
                time.sleep(0.1)
            data = ser.read(1)#must read the bytes and put in a file
            f.write(data)
            numBytes=numBytes+1
        f.close()
        print("\nDone\n")
    #Burn EPROM, see schematic at my website
    if(option==2):
        name=input("What's the name of the file?")
        print(name)
        f = open(name, 'rb')
        for i in range(numsectors):
            ser.write(b"\x55")
            ser.write(bytes("w","ASCII" ))
            time.sleep(0.001)
            #send address of the block first
            ser.write(struct.pack(">B",i>>8))
            CHK=i>>8
            time.sleep(0.001)
            ser.write(struct.pack(">B",i&0xFF))
            CHK^=i&0xFF
            time.sleep(0.001)
            data=f.read(128);
            #print(data)

            #Gets checksum from xoring the package
            for j in range(len(data)):
                CHK=CHK^data[j]

            time.sleep(0.001)
            print("Writing data. Current porcentage:{:.2%}".format(i/numsectors),end='\r')
            print("CHK:", ~CHK)
            response=~CHK

            #keeps trying while the replied checksum is not correct
            while response!=CHK:
                ser.write(data)
                ser.write(struct.pack(">B",CHK&0xFF))
                timeout=60
                while ser.inWaiting()==0:
                    time.sleep(0.01)
                    timeout=timeout-1
                    if timeout==0:
                        print("could not get a response, please start again\n")
                        break
                CHKBCK = ser.read(1)
                
                if(len(CHKBCK) > 0):
                    response=ord(CHKBCK)
                    if response!=CHK:
                        print("wrong checksum, sending chunk again\n")
        f.close()

    #Just some info
    if(option==3):
        print("Writing zero's to EPROM")
        for i in range(numsectors):
            ser.write(b"\x55")
            ser.write(bytes("w","ASCII" ))
            time.sleep(0.001)
            #send address of the block first
            ser.write(struct.pack(">B",i>>8))
            CHK=i>>8
            time.sleep(0.001)
            ser.write(struct.pack(">B",i&0xFF))
            CHK^=i&0xFF
            time.sleep(0.001)
            data=bytearray(128)

            for j in range(len(data)):
                CHK=CHK^data[j]

            time.sleep(0.001)
            print("Writing data. Current porcentage:{:.2%}".format(i/numsectors),end='\r')
            print("CHK:", CHK)
            response=~CHK

            #keeps trying while the replied checksum is not correct
            while response!=CHK:
                ser.write(data)
                ser.write(struct.pack(">B",CHK&0xFF))
                timeout=60
                while ser.inWaiting()==0:
                    time.sleep(0.01)
                    timeout=timeout-1
                    if timeout==0:
                        print("could not get a response, please start again\n")
                        break
                CHKBCK = ser.read(1)
                
                if(len(CHKBCK) > 0):
                    response=ord(CHKBCK)
                    if response!=CHK:
                        print("wrong checksum, sending chunk again\n")
        f.close()

    #Blank check
    if(option==4):
        #same as reading
        ser.flushInput()
        ser.write(b"\x55")
        ser.write(bytes("r","ASCII"))
        numBytes=0
        blank=1
        while (numBytes<romsize):
            while ser.inWaiting()==0:
                print("Reading from eprom. Current porcentage:{:.2%}".format(numBytes/romsize),end='\r')
                time.sleep(0.1)
            data = ser.read(1)
            numBytes=numBytes+1
            if ord(data)!=255:
                blank=0
                break
        #Ends check on first byte not erased
        if blank==1:
            print("\nThe chip is blank\n")
        else:
            print("\nThe chip seems to contain data\n")
        print("Done\n")
    #Change size of EPROM, for reading EPROMs other than 1MB
    if(option==5):
        print("Current eprom size:",romsize/(1024*1024),"MB\n")
        megs=float(input("Please insert the size of the eprom in Megabytes"))
        romsize=megs*1024*1024
        numsectors=int(romsize/128) # I am sending data in 128 byte chunks
        if megs>1:
            print("Eprom size changed to ",romsize/(1024*1024),"MB\n")
        else:
            print("Eprom size changed to ",romsize/(1024),"KB\n")
    #This is for checking if the eprom was programmed right
    if(option==6):
        #Reads each byte and compares with a byte in the file
        print("This compares a eprom with a file in the script folder\n")
        name=input("\nWhat's the name of the file?\n")
        f = open(name, 'rb')
        ser.flushInput()
        ser.write(b"\x55")
        ser.write(bytes("r","ASCII"))
        numBytes=0
        while (numBytes<romsize):
            while ser.inWaiting()==0:
                print("Reading from eprom. Current porcentage:{:.2%}".format(numBytes/romsize),end='\r')
                time.sleep(0.01)
            eprom_byte = ser.read(1)
            file_byte = f.read(1)
            if(eprom_byte!=file_byte):
                #the \033[031m and \033[0m sequence are ansi sequences that turn text red and cancel it respectively
                #I dont know how windows handle them
                print("\n\033[31mFound mismatch at",hex(f.tell()))
                print("- eprom byte:",hex(ord(eprom_byte)),"- file byte:",hex(ord(file_byte)),"\033[0m\n")
            numBytes=numBytes+1
        print("\nDone\n")
    if(option==7):
        print("See ya!")
        break
