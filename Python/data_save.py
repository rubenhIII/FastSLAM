import serial
import NNet
import pandas as pd
from threading import Thread, Event

def read_serial_data(event, ser, f):
    data_list = []
    while True:
        if ser.in_waiting > 0 :
            data = ser.readline()
            data = data.decode(('utf-8;')).rstrip()
            data_float = map(lambda x: float(x), str(data).split(" "))
            print(data_float)
            if data != "" and data != "\n":
                nnet_res = NNet.eval_NN(pd.DataFrame(data_float)[0])
                print(nnet_res)
           
            data_list.append(data + '\n')
            print(str(data))   
        if event.is_set():
            f.writelines(data_list)
            f.close()
            break
    print("Exiting...")
    return False

serial_port = '/dev/pts/7'
file = "./results/data.txt"
answ = input("The file data will be override, continue? (y/n) ")

if answ == "y":
    f = open(file, "w")
    ser = serial.Serial(port = serial_port, baudrate = 9600)
    eventStop = Event()
    t1 = Thread(target=read_serial_data, args=(eventStop, ser, f, ))
    t1.start()
    
    while answ != "x":
        answ = input("Enter x to exit: ")
        values = bytearray(answ, "ascii")
        ser.write(values)
        if answ == "x":
            eventStop.set()
            t1.join()

